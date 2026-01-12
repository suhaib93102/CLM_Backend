"""
Search Models - Complete Ingestion Pipeline
Implements document storage, chunking, embeddings, and hybrid search
"""
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from pgvector.django import VectorField
import uuid


class DocumentModel(models.Model):
    """
    Document Storage - Base document ingestion
    Stores original documents before processing
    
    Flow:
    1. User uploads PDF/DOCX/image
    2. Store file path and metadata
    3. Process: OCR → extraction → chunks
    4. Generate embeddings for each chunk
    """
    DOCUMENT_TYPE_CHOICES = (
        ('contract', 'Contract'),
        ('template', 'Template'),
        ('workflow', 'Workflow'),
        ('approval', 'Approval'),
    )
    
    STATUS_CHOICES = (
        ('uploaded', 'Uploaded'),
        ('processing', 'Processing'),
        ('ocr_pending', 'OCR Pending'),
        ('indexed', 'Indexed'),
        ('failed', 'Failed'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=255, db_index=True)
    entity_type = models.CharField(max_length=50, choices=DOCUMENT_TYPE_CHOICES)
    entity_id = models.UUIDField(null=True, blank=True)  # Reference to original entity
    
    # Document metadata
    title = models.CharField(max_length=500)
    file_path = models.TextField()  # S3/local path
    file_type = models.CharField(max_length=20)  # pdf, docx, txt, jpg, png
    file_size = models.IntegerField()  # bytes
    
    # Processing status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='uploaded')
    extracted_text = models.TextField(blank=True, null=True)  # OCR output
    processing_error = models.TextField(blank=True, null=True)  # Error message
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documents'
        app_label = 'search'
        indexes = [
            models.Index(fields=['tenant_id', 'status'], name='doc_tenant_status'),
            models.Index(fields=['entity_id'], name='doc_entity_lookup'),
        ]
    
    def __str__(self):
        return f"{self.entity_type}: {self.title}"


class DocumentChunkModel(models.Model):
    """
    Document Chunks - Chunk-level processing
    Each chunk has own embedding for precise search
    
    Why chunks?
    - Clauses matter more than full documents
    - Better embedding precision
    - Enables clause-level search
    - Improves both FTS and semantic ranking
    """
    CHUNK_TYPE_CHOICES = (
        ('clause', 'Legal Clause'),
        ('paragraph', 'Paragraph'),
        ('section', 'Section'),
        ('heading', 'Heading'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=255, db_index=True)
    document = models.ForeignKey(DocumentModel, on_delete=models.CASCADE, related_name='chunks')
    
    # Chunk content
    chunk_type = models.CharField(max_length=20, choices=CHUNK_TYPE_CHOICES, default='paragraph')
    title = models.CharField(max_length=255, blank=True)  # Section title if applicable
    content = models.TextField()  # Actual chunk text
    chunk_index = models.IntegerField()  # Position in document (0, 1, 2, ...)
    
    # Search fields
    search_vector = SearchVectorField(null=True)  # PostgreSQL FTS
    embedding = VectorField(dimensions=768, null=True, blank=True)  # Gemini/OpenAI embeddings
    
    # Metadata
    keywords = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)  # {clause_type, section, page, etc}
    
    # Scoring
    fts_rank = models.FloatField(default=0.0)  # FTS relevance
    semantic_score = models.FloatField(default=0.0)  # Semantic relevance
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    embedding_model = models.CharField(max_length=50, default='gemini')  # Track which model
    
    class Meta:
        db_table = 'document_chunks'
        app_label = 'search'
        indexes = [
            GinIndex(fields=['search_vector'], name='chunk_fts_gin'),
            models.Index(fields=['tenant_id', 'chunk_type'], name='chunk_tenant_type'),
            models.Index(fields=['document'], name='chunk_document_lookup'),
        ]
    
    def __str__(self):
        return f"Chunk {self.chunk_index}: {self.title or self.content[:50]}"


class SearchIndexModel(models.Model):
    """
    Search Index - Optimized for fast queries
    Denormalized view of DocumentChunkModel for performance
    
    Contains:
    - Full-Text Search vector (PostgreSQL native)
    - Semantic embeddings (pgvector)
    - Ranking scores (FTS, semantic, hybrid, boost)
    """
    ENTITY_TYPE_CHOICES = (
        ('contract', 'Contract'),
        ('template', 'Template'),
        ('workflow', 'Workflow'),
        ('approval', 'Approval'),
        ('document', 'Document'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=255, db_index=True)
    
    # Source reference
    entity_type = models.CharField(max_length=50, choices=ENTITY_TYPE_CHOICES)
    entity_id = models.UUIDField(db_index=True)
    chunk = models.ForeignKey(DocumentChunkModel, on_delete=models.CASCADE, null=True, blank=True)
    
    # Content
    title = models.CharField(max_length=500)
    content = models.TextField()
    keywords = models.JSONField(default=list)
    metadata = models.JSONField(default=dict)
    
    # Search vectors
    search_vector = SearchVectorField(null=True)  # FTS
    embedding = VectorField(dimensions=768, null=True, blank=True)  # Semantic
    
    # Ranking scores
    fts_rank = models.FloatField(default=0.0)
    semantic_score = models.FloatField(default=0.0)
    hybrid_score = models.FloatField(default=0.0)  # Combined score
    boost_score = models.FloatField(default=1.0)  # Metadata boost (recency, status, etc)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'search_indices'
        app_label = 'search'
        indexes = [
            GinIndex(fields=['search_vector'], name='search_index_gin'),
            models.Index(fields=['tenant_id', 'entity_type'], name='search_tenant_entity'),
            models.Index(fields=['entity_id'], name='search_entity_lookup'),
        ]
    
    def calculate_hybrid_score(self, fts_weight=0.3, semantic_weight=0.6, boost_weight=0.1):
        """
        Calculate hybrid relevance score
        
        Formula:
        hybrid_score = (0.3 × fts_rank) + (0.6 × semantic_score) + (0.1 × boost_score)
        
        Weights:
        - FTS: 30% - Fast & precise, good for exact matches
        - Semantic: 60% - Meaning-based, good for paraphrases
        - Boost: 10% - Metadata (recency, status, popularity)
        """
        self.hybrid_score = (
            fts_weight * self.fts_rank +
            semantic_weight * self.semantic_score +
            boost_weight * self.boost_score
        )
        return self.hybrid_score
    
    def __str__(self):
        return f"{self.entity_type}: {self.title}"


class SearchAnalyticsModel(models.Model):
    """
    Search Analytics - Track all queries for insights
    
    Tracks:
    - Query type (FTS, semantic, hybrid, similar)
    - Performance metrics
    - User feedback for improvement
    - Click-through rates
    """
    QUERY_TYPE_CHOICES = (
        ('full_text', 'Full-Text (FTS)'),
        ('semantic', 'Semantic (Embeddings)'),
        ('hybrid', 'Hybrid (FTS + Semantic)'),
        ('faceted', 'Faceted Navigation'),
        ('similar', 'Find Similar'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tenant_id = models.CharField(max_length=255, db_index=True)
    user_id = models.CharField(max_length=255, null=True, blank=True)
    
    # Query details
    query = models.TextField()
    query_type = models.CharField(max_length=20, choices=QUERY_TYPE_CHOICES)
    
    # Results
    results_count = models.IntegerField(default=0)
    selected_result_id = models.UUIDField(null=True, blank=True)  # Which result user clicked
    time_spent_ms = models.IntegerField(default=0)  # How long user spent on results
    
    # Performance
    response_time_ms = models.IntegerField(default=0)  # Query execution time
    embedding_api_time_ms = models.IntegerField(default=0)  # Just API call time
    
    # Feedback
    was_helpful = models.BooleanField(null=True, blank=True)  # User feedback
    feedback_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    
    class Meta:
        db_table = 'search_analytics'
        app_label = 'search'
        indexes = [
            models.Index(fields=['tenant_id', 'created_at'], name='analytics_tenant_date'),
            models.Index(fields=['query_type'], name='analytics_type'),
            models.Index(fields=['user_id', 'created_at'], name='analytics_user_date'),
        ]
    
    def __str__(self):
        return f"{self.query_type}: {self.query[:50]}"

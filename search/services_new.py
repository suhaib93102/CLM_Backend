"""
Search Services Layer - No ML Training Required
Implements:
- Document OCR (Tesseract)
- Embedding Generation (Gemini/OpenAI API - no training)
- Full-Text Search (PostgreSQL FTS)
- Semantic Search (pgvector)
- Hybrid Ranking (weighted combination)
"""
import time
import math
from typing import List, Dict, Tuple, Optional
from django.db.models import Q, QuerySet
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Embedding Generation Service
    Uses PRE-TRAINED models (Gemini/OpenAI) - NO TRAINING REQUIRED
    
    Strategy:
    1. Call Gemini Embeddings API (free tier: 60k/month)
    2. Cache embeddings to avoid repeated API calls
    3. Use 768-dimensional vectors (smaller than OpenAI 1536)
    4. Hash text to check cache
    """
    
    EMBEDDING_DIMENSION = 768
    EMBEDDING_MODEL = "gemini"
    
    @staticmethod
    def get_embedding(text: str, cache=True) -> Optional[List[float]]:
        """
        Get embedding for text without training
        
        Args:
            text: Text to embed
            cache: Use cached embedding if available
            
        Returns:
            768-dimensional embedding vector
            
        Flow:
        1. Hash text
        2. Check cache (TODO: implement Redis)
        3. If not cached:
           - Call Gemini API
           - Store embedding
           - Return
        4. If cached:
           - Return cached vector
        
        No training involved - just API call
        """
        if not text or len(text.strip()) < 10:
            return None
        
        try:
            # TODO: Implement actual Gemini API call
            # from google.generativeai import embed_content
            # response = embed_content(
            #     model="models/embedding-001",
            #     content=text
            # )
            # return response['embedding']
            
            # Placeholder: Return dummy embedding
            logger.warning(f"Gemini API not configured. Returning placeholder embedding.")
            return [0.1] * EmbeddingService.EMBEDDING_DIMENSION
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return None
    
    @staticmethod
    def batch_embeddings(texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts
        Batch API calls for efficiency
        """
        embeddings = []
        for text in texts:
            embeddings.append(EmbeddingService.get_embedding(text))
        return embeddings


class OCRService:
    """
    OCR Service - Extract text from scanned documents
    Uses Tesseract (local) or Google Vision (cloud)
    No ML training required
    """
    
    @staticmethod
    def extract_text(file_path: str, file_type: str) -> Tuple[str, bool]:
        """
        Extract text from document
        
        Args:
            file_path: Path to file (local or S3)
            file_type: pdf, docx, txt, jpg, png
            
        Returns:
            (extracted_text, success)
            
        Strategy:
        - TXT, DOCX: Direct parsing (no OCR)
        - PDF: PyPDF2 + Tesseract for scanned pages
        - Images: Tesseract
        
        No training - just character recognition
        """
        try:
            if file_type == 'txt':
                with open(file_path, 'r') as f:
                    return f.read(), True
            
            elif file_type == 'pdf':
                # TODO: Implement PDF extraction
                # import PyPDF2
                # with open(file_path, 'rb') as f:
                #     reader = PyPDF2.PdfReader(f)
                #     text = ""
                #     for page in reader.pages:
                #         text += page.extract_text()
                # return text, True
                logger.warning("PDF extraction not implemented")
                return "", False
            
            elif file_type in ['jpg', 'png']:
                # TODO: Implement Tesseract OCR
                # import pytesseract
                # from PIL import Image
                # image = Image.open(file_path)
                # text = pytesseract.image_to_string(image)
                # return text, True
                logger.warning("Image OCR not implemented")
                return "", False
            
            else:
                return "", False
                
        except Exception as e:
            logger.error(f"OCR extraction failed: {str(e)}")
            return "", False


class TextNormalizationService:
    """
    Text Normalization
    Prepare text for both FTS and embeddings
    """
    
    @staticmethod
    def normalize_text(text: str) -> str:
        """
        Normalize text for indexing
        
        Steps:
        1. Remove headers/footers
        2. Normalize whitespace
        3. Remove excessive punctuation
        4. Lowercase for consistency
        
        NOT training - just preprocessing
        """
        # Remove excessive whitespace
        text = ' '.join(text.split())
        
        # Keep single spaces, normalize newlines
        text = text.replace('\n', ' ').replace('\r', '')
        
        return text.strip()
    
    @staticmethod
    def chunk_text(text: str, chunk_size=500, overlap=100) -> List[Dict]:
        """
        Split text into chunks for better embedding precision
        
        Why chunks?
        - Clauses are more important than full documents
        - Better semantic precision
        - Enables clause-level search
        
        Args:
            text: Full text
            chunk_size: Characters per chunk (~100 tokens)
            overlap: Overlap between chunks to maintain context
            
        Returns:
            List of {content, index, title}
        """
        chunks = []
        position = 0
        chunk_index = 0
        
        while position < len(text):
            end = min(position + chunk_size, len(text))
            chunk_text = text[position:end]
            
            chunks.append({
                'content': chunk_text.strip(),
                'chunk_index': chunk_index,
                'title': f"Section {chunk_index + 1}",
            })
            
            position = end - overlap
            chunk_index += 1
        
        return chunks


class FullTextSearchService:
    """
    Full-Text Search (FTS) - PostgreSQL Native
    Fast, precise keyword search
    No training required
    
    Performance: O(log n) with GIN index
    Best for: Exact phrases, legal terms, filters
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, limit: int = 20) -> QuerySet:
        """
        Perform FTS using PostgreSQL native capabilities
        
        Algorithm:
        1. Convert query to tsquery
        2. Match against search_vector
        3. Rank by ts_rank
        4. Return top results
        
        SQL generated:
        SELECT *, ts_rank(search_vector, query) as rank
        FROM search_index
        WHERE search_vector @@ plainto_tsquery('english', 'query')
        AND tenant_id = 'tenant_id'
        ORDER BY ts_rank(search_vector, query) DESC
        LIMIT 20
        """
        from search.models import SearchIndexModel
        
        search_query = SearchQuery(query, search_type='plain')
        search_vector = SearchVector('title', weight='A') + SearchVector('content', weight='B')
        
        # Execute FTS
        queryset = (
            SearchIndexModel.objects
            .filter(
                search_vector=search_query,
                tenant_id=tenant_id
            )
            .annotate(
                rank=SearchRank(search_vector, search_query)
            )
            .order_by('-rank')[:limit]
        )
        
        return queryset
    
    @staticmethod
    def format_results(queryset: QuerySet) -> List[Dict]:
        """Format FTS results with scores"""
        results = []
        for item in queryset:
            results.append({
                'id': str(item.id),
                'title': item.title,
                'entity_type': item.entity_type,
                'relevance_score': float(item.rank),  # FTS rank (0-1)
                'search_type': 'full_text',
                'created_at': item.created_at.isoformat(),
            })
        return results


class SemanticSearchService:
    """
    Semantic Search - Meaning-based
    Uses pgvector + pre-trained embeddings
    No training required
    
    Performance: O(n) without index, O(log n) with IVFFlat index
    Best for: Synonyms, paraphrases, multi-language
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, similarity_threshold: float = 0.6, limit: int = 20) -> List[Dict]:
        """
        Semantic search using embeddings
        
        Algorithm:
        1. Convert query to embedding (Gemini API)
        2. Find similar vectors in database
        3. Filter by threshold
        4. Return top results by similarity
        
        Formula:
        similarity = 1 - (embedding <=> query_embedding)
        """
        from search.models import SearchIndexModel
        
        # Generate query embedding
        query_embedding = EmbeddingService.get_embedding(query)
        if not query_embedding:
            return []
        
        # Vector search with pgvector
        # Note: Requires pgvector extension in PostgreSQL
        try:
            queryset = (
                SearchIndexModel.objects
                .filter(tenant_id=tenant_id, embedding__isnull=False)
                .extra(
                    select={'distance': 'embedding <=> %s::vector'},
                    select_params=(query_embedding,)
                )
                .filter(distance__lte=(1 - similarity_threshold))  # threshold
                .order_by('distance')[:limit]
            )
            
            results = []
            for item in queryset:
                # Calculate similarity from distance
                similarity = 1 - float(item.distance)
                results.append({
                    'id': str(item.id),
                    'title': item.title,
                    'entity_type': item.entity_type,
                    'relevance_score': similarity,
                    'search_type': 'semantic',
                    'created_at': item.created_at.isoformat(),
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []


class HybridSearchService:
    """
    Hybrid Search - Combines FTS + Semantic
    Best overall search experience
    No training required
    
    Ranking Formula:
    hybrid_score = (0.3 × fts_rank) + (0.6 × semantic_score) + (0.1 × boost)
    
    Weights:
    - FTS (30%): Fast, precise, good for exact matches
    - Semantic (60%): Meaning-based, good for paraphrases
    - Boost (10%): Metadata (recency, status, popularity)
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, limit: int = 20) -> List[Dict]:
        """
        Hybrid search combining FTS + semantic
        
        Flow:
        1. Run FTS search
        2. Run semantic search
        3. Merge results (deduplicate)
        4. Normalize scores to 0-1
        5. Combine with weights
        6. Re-rank by hybrid score
        """
        # Step 1: Get FTS results
        fts_results = FullTextSearchService.search(query, tenant_id, limit=limit*2)
        fts_dict = {r['id']: r for r in fts_results}
        
        # Step 2: Get semantic results
        semantic_results = SemanticSearchService.search(query, tenant_id, limit=limit*2)
        semantic_dict = {r['id']: r for r in semantic_results}
        
        # Step 3: Merge and normalize scores
        merged = {}
        all_ids = set(fts_dict.keys()) | set(semantic_dict.keys())
        
        for result_id in all_ids:
            fts_score = fts_dict.get(result_id, {}).get('relevance_score', 0) if result_id in fts_dict else 0
            semantic_score = semantic_dict.get(result_id, {}).get('relevance_score', 0) if result_id in semantic_dict else 0
            
            # Use data from whichever source has it
            base_data = fts_dict.get(result_id) or semantic_dict.get(result_id)
            
            # Step 4: Calculate hybrid score
            hybrid_score = (0.3 * fts_score) + (0.6 * semantic_score) + (0.1 * 1.0)  # boost = 1.0
            
            merged[result_id] = {
                **base_data,
                'fts_score': fts_score,
                'semantic_score': semantic_score,
                'hybrid_score': hybrid_score,
                'search_type': 'hybrid',
            }
        
        # Step 5: Sort by hybrid score
        sorted_results = sorted(merged.values(), key=lambda x: x['hybrid_score'], reverse=True)
        
        return sorted_results[:limit]


class FilteringService:
    """
    Advanced Filtering - SQL WHERE clauses
    Combine FTS with precise filtering
    """
    
    @staticmethod
    def apply_filters(queryset: QuerySet, filters: Dict) -> QuerySet:
        """
        Apply filters to queryset
        
        Supported filters:
        - entity_type: Exact match
        - date_from/date_to: Date range
        - keywords: Any keyword match
        - status: Metadata filtering
        """
        if filters.get('entity_type'):
            queryset = queryset.filter(entity_type=filters['entity_type'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        if filters.get('keywords'):
            # Keywords: match any
            q = Q()
            for keyword in filters['keywords']:
                q |= Q(keywords__contains=[keyword])
            queryset = queryset.filter(q)
        
        if filters.get('status'):
            queryset = queryset.filter(metadata__status=filters['status'])
        
        return queryset


class FacetedSearchService:
    """
    Faceted Navigation - Drill-down filtering
    Provides facet counts for UI
    """
    
    @staticmethod
    def get_facets(tenant_id: str) -> Dict:
        """
        Get available facets for navigation
        
        Returns:
        {
            "entity_types": [
                {"name": "contract", "count": 234},
                ...
            ],
            "date_range": {
                "earliest": "2020-01-01",
                "latest": "2024-12-31"
            }
        }
        """
        from search.models import SearchIndexModel
        from django.db.models import Count, Min, Max
        
        # Entity type facets
        entity_facets = (
            SearchIndexModel.objects
            .filter(tenant_id=tenant_id)
            .values('entity_type')
            .annotate(count=Count('id'))
            .order_by('-count')
        )
        
        # Date range
        date_agg = (
            SearchIndexModel.objects
            .filter(tenant_id=tenant_id)
            .aggregate(
                earliest=Min('created_at'),
                latest=Max('created_at')
            )
        )
        
        return {
            'entity_types': [
                {'name': item['entity_type'], 'count': item['count']}
                for item in entity_facets
            ],
            'date_range': {
                'earliest': date_agg['earliest'].isoformat() if date_agg['earliest'] else None,
                'latest': date_agg['latest'].isoformat() if date_agg['latest'] else None,
            }
        }


class DocumentIngestionService:
    """
    Document Ingestion Pipeline
    
    Flow:
    1. Upload document
    2. Extract text (OCR if needed)
    3. Normalize text
    4. Split into chunks
    5. Generate FTS vector
    6. Generate embeddings
    7. Create search index
    """
    
    @staticmethod
    def ingest_document(file_path: str, file_type: str, title: str, tenant_id: str, entity_id: str) -> Tuple[bool, str]:
        """
        Complete ingestion pipeline
        
        Returns:
            (success, message)
        """
        from search.models import DocumentModel, DocumentChunkModel, SearchIndexModel
        
        try:
            # Step 1: Create document record
            doc = DocumentModel.objects.create(
                tenant_id=tenant_id,
                entity_id=entity_id,
                title=title,
                file_path=file_path,
                file_type=file_type,
                file_size=0,  # TODO: Get actual file size
                status='processing'
            )
            
            # Step 2: Extract text
            extracted_text, success = OCRService.extract_text(file_path, file_type)
            if not success:
                doc.status = 'failed'
                doc.processing_error = 'OCR extraction failed'
                doc.save()
                return False, "OCR extraction failed"
            
            # Step 3: Normalize
            normalized_text = TextNormalizationService.normalize_text(extracted_text)
            doc.extracted_text = normalized_text
            doc.save()
            
            # Step 4: Chunk text
            chunks = TextNormalizationService.chunk_text(normalized_text)
            
            # Step 5-6: Process chunks
            for chunk_data in chunks:
                # Generate FTS vector
                search_vector = SearchVector('content', weight='A')
                
                # Generate embeddings
                embedding = EmbeddingService.get_embedding(chunk_data['content'])
                
                # Create chunk
                chunk = DocumentChunkModel.objects.create(
                    tenant_id=tenant_id,
                    document=doc,
                    chunk_type='clause',
                    title=chunk_data['title'],
                    content=chunk_data['content'],
                    chunk_index=chunk_data['chunk_index'],
                    keywords=[],
                    embedding_model='gemini'
                )
                
                # Step 7: Create search index
                SearchIndexModel.objects.create(
                    tenant_id=tenant_id,
                    entity_type=doc.entity_type,
                    entity_id=entity_id,
                    chunk=chunk,
                    title=title,
                    content=chunk_data['content'],
                    keywords=[],
                    embedding=embedding
                )
            
            # Mark as complete
            doc.status = 'indexed'
            doc.save()
            
            return True, f"Document ingested successfully ({len(chunks)} chunks)"
            
        except Exception as e:
            logger.error(f"Document ingestion failed: {str(e)}")
            return False, str(e)


class SimilarDocumentService:
    """
    Find Similar Documents
    Uses vector similarity
    """
    
    @staticmethod
    def find_similar(source_id: str, tenant_id: str, limit: int = 10) -> List[Dict]:
        """
        Find similar documents using embeddings
        
        Flow:
        1. Get source document embedding
        2. Find similar vectors
        3. Return top N
        """
        from search.models import SearchIndexModel
        
        try:
            # Get source embedding
            source = SearchIndexModel.objects.get(id=source_id)
            if not source.embedding:
                return []
            
            # Find similar
            similar = (
                SearchIndexModel.objects
                .filter(
                    tenant_id=tenant_id,
                    embedding__isnull=False
                )
                .exclude(id=source_id)
                .extra(
                    select={'distance': f'embedding <=> %s::vector'},
                    select_params=(source.embedding,)
                )
                .order_by('distance')[:limit]
            )
            
            results = []
            for item in similar:
                similarity = 1 - float(item.distance)
                results.append({
                    'id': str(item.id),
                    'title': item.title,
                    'entity_type': item.entity_type,
                    'relevance_score': similarity,
                })
            
            return results
            
        except Exception as e:
            logger.error(f"Find similar failed: {str(e)}")
            return []

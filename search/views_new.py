"""
Search Views - Corrected Architecture
Implements document ingestion and hybrid search endpoints
No ML training required - uses pre-trained embeddings API
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import time
from .services_new import (
    DocumentIngestionService,
    FullTextSearchService,
    SemanticSearchService,
    HybridSearchService,
    FilteringService,
    FacetedSearchService,
    SimilarDocumentService,
)
from .models_new import SearchAnalyticsModel


class DocumentUploadView(APIView):
    """
    Document Upload and Ingestion
    Endpoint: POST /api/search/upload/
    
    Flow:
    1. User uploads document (PDF/DOCX/image)
    2. Extract text (OCR if needed)
    3. Normalize text
    4. Split into chunks
    5. Generate embeddings (Gemini API)
    6. Create FTS indexes
    7. Return success
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Upload and ingest document
        
        Request:
        - file: Document file (PDF/DOCX/image)
        - title: Document title
        - entity_type: contract/template/workflow
        - entity_id: Optional reference ID
        
        Response:
        {
            "success": true,
            "message": "Document ingested successfully (5 chunks)",
            "document_id": "uuid"
        }
        """
        try:
            if 'file' not in request.FILES:
                return Response({
                    'success': False,
                    'message': 'No file provided'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            file_obj = request.FILES['file']
            title = request.data.get('title', file_obj.name)
            entity_type = request.data.get('entity_type', 'document')
            entity_id = request.data.get('entity_id')
            
            tenant_id = request.user.tenant_id
            
            # Save file temporarily
            file_path = f"/tmp/{file_obj.name}"
            # TODO: Upload to S3/cloud storage
            
            # Ingest document
            success, message = DocumentIngestionService.ingest_document(
                file_path=file_path,
                file_type=file_obj.name.split('.')[-1],
                title=title,
                tenant_id=tenant_id,
                entity_id=entity_id
            )
            
            if not success:
                return Response({
                    'success': False,
                    'message': message
                }, status=status.HTTP_400_BAD_REQUEST)
            
            return Response({
                'success': True,
                'message': message
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class FullTextSearchView(APIView):
    """
    Full-Text Search (FTS)
    Endpoint: GET /api/search/fts/?q=query
    
    Strategy: PostgreSQL Full-Text Search
    - Fast & precise keyword matching
    - GIN index for O(log n) lookup
    - Best for: exact phrases, legal terms
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Full-text keyword search
        
        Query Parameters:
        - q: Search query (min 2 chars)
        - limit: Results limit (default 20)
        - filters: JSON filters (optional)
        
        Response:
        {
            "search_type": "full_text",
            "results": [...],
            "count": 10,
            "response_time_ms": 45
        }
        """
        start_time = time.time()
        
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        
        if not query or len(query) < 2:
            return Response({
                'error': 'Query must be at least 2 characters',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = request.user.tenant_id
        
        # FTS search
        fts_results = FullTextSearchService.search(query, tenant_id, limit=limit)
        formatted_results = FullTextSearchService.format_results(fts_results)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=getattr(request.user, 'user_id', None),
            query=query,
            query_type='full_text',
            results_count=len(formatted_results),
            response_time_ms=response_time_ms
        )
        
        return Response({
            'search_type': 'full_text',
            'query': query,
            'results': formatted_results,
            'count': len(formatted_results),
            'response_time_ms': response_time_ms,
            'strategy': 'PostgreSQL FTS + GIN Index',
            'note': 'Fast, precise keyword matching'
        })


class SemanticSearchView(APIView):
    """
    Semantic Search with Embeddings
    Endpoint: GET /api/search/semantic/?q=query
    
    Strategy: Meaning-based search
    - Uses pre-trained Gemini embeddings (no training)
    - pgvector for similarity
    - Best for: synonyms, paraphrases, fuzzy matching
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Semantic search using embeddings
        
        Query Parameters:
        - q: Search query
        - threshold: Similarity threshold (0-1, default 0.6)
        - limit: Results limit (default 20)
        
        Response:
        {
            "search_type": "semantic",
            "results": [...],
            "count": 8,
            "response_time_ms": 120
        }
        """
        start_time = time.time()
        
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        threshold = float(request.query_params.get('threshold', 0.6))
        
        if not query:
            return Response({
                'error': 'Query is required',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = request.user.tenant_id
        
        # Semantic search
        semantic_results = SemanticSearchService.search(
            query, 
            tenant_id, 
            similarity_threshold=threshold,
            limit=limit
        )
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=getattr(request.user, 'user_id', None),
            query=query,
            query_type='semantic',
            results_count=len(semantic_results),
            response_time_ms=response_time_ms,
            embedding_api_time_ms=response_time_ms
        )
        
        return Response({
            'search_type': 'semantic',
            'query': query,
            'results': semantic_results,
            'count': len(semantic_results),
            'response_time_ms': response_time_ms,
            'threshold': threshold,
            'strategy': 'pgvector + Pre-trained Embeddings (Gemini)',
            'note': 'Meaning-based search, handles synonyms and paraphrases'
        })


class HybridSearchView(APIView):
    """
    Hybrid Search - Best overall
    Endpoint: POST /api/search/hybrid/
    
    Strategy: Combines FTS + Semantic
    - FTS (30%): Precision, exact matches
    - Semantic (60%): Meaning, synonyms
    - Boost (10%): Metadata (recency, status)
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Hybrid search combining FTS + semantic
        
        Request Body:
        {
            "query": "auto-renewal clauses",
            "limit": 20,
            "filters": {...}
        }
        
        Response:
        {
            "search_type": "hybrid",
            "results": [...],
            "count": 12,
            "response_time_ms": 180,
            "ranking_formula": "0.3*FTS + 0.6*Semantic + 0.1*Boost"
        }
        """
        start_time = time.time()
        
        query = request.data.get('query', '').strip()
        limit = request.data.get('limit', 20)
        
        if not query:
            return Response({
                'error': 'Query is required',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = request.user.tenant_id
        
        # Hybrid search
        hybrid_results = HybridSearchService.search(query, tenant_id, limit=limit)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=getattr(request.user, 'user_id', None),
            query=query,
            query_type='hybrid',
            results_count=len(hybrid_results),
            response_time_ms=response_time_ms
        )
        
        return Response({
            'search_type': 'hybrid',
            'query': query,
            'results': hybrid_results,
            'count': len(hybrid_results),
            'response_time_ms': response_time_ms,
            'ranking_formula': '0.3*FTS + 0.6*Semantic + 0.1*Boost',
            'strategy': 'PostgreSQL FTS (30%) + pgvector Embeddings (60%) + Metadata Boost (10%)',
            'note': 'Best overall search - balances precision and meaning'
        })


class AdvancedSearchView(APIView):
    """
    Advanced Search with Filters
    Endpoint: POST /api/search/advanced/
    
    Strategy: FTS + SQL WHERE clauses
    Enables complex filtering
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Advanced search with filters
        
        Request Body:
        {
            "query": "renewal clause",
            "filters": {
                "entity_type": "contract",
                "date_from": "2023-01-01",
                "date_to": "2024-12-31",
                "status": "active"
            },
            "limit": 20
        }
        """
        query = request.data.get('query', '').strip()
        filters = request.data.get('filters', {})
        limit = request.data.get('limit', 20)
        
        tenant_id = request.user.tenant_id
        
        # FTS search
        if query:
            queryset = FullTextSearchService.search(query, tenant_id, limit=limit*2)
        else:
            from .models_new import SearchIndexModel
            queryset = SearchIndexModel.objects.filter(tenant_id=tenant_id)
        
        # Apply filters
        queryset = FilteringService.apply_filters(queryset, filters)
        
        # Get results
        results = FullTextSearchService.format_results(queryset[:limit])
        
        return Response({
            'search_type': 'advanced',
            'query': query,
            'results': results,
            'count': len(results),
            'filters_applied': filters,
            'strategy': 'PostgreSQL FTS + SQL WHERE clauses'
        })


class FacetsView(APIView):
    """
    Get Available Facets for Navigation
    Endpoint: GET /api/search/facets/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get facets for drill-down navigation
        """
        tenant_id = request.user.tenant_id
        facets = FacetedSearchService.get_facets(tenant_id)
        
        return Response({
            'facets': facets,
            'strategy': 'SQL GROUP BY aggregations'
        })


class SimilarDocumentsView(APIView):
    """
    Find Similar Documents
    Endpoint: GET /api/search/similar/{document_id}/
    
    Strategy: Vector similarity
    Uses embeddings to find semantically similar documents
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, document_id):
        """
        Find documents similar to the given document
        
        Query Parameters:
        - limit: Max results (default 10)
        
        Response:
        {
            "source_id": "uuid",
            "similar_documents": [...],
            "count": 5,
            "strategy": "Vector similarity (embeddings)"
        }
        """
        limit = int(request.query_params.get('limit', 10))
        tenant_id = request.user.tenant_id
        
        similar = SimilarDocumentService.find_similar(
            document_id, 
            tenant_id, 
            limit=limit
        )
        
        return Response({
            'source_id': document_id,
            'similar_documents': similar,
            'count': len(similar),
            'strategy': 'Vector similarity using embeddings'
        })


class SearchAnalyticsView(APIView):
    """
    Search Analytics
    Endpoint: GET /api/search/analytics/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get search analytics and metrics
        """
        tenant_id = request.user.tenant_id
        from django.db.models import Avg, Count
        
        analytics = SearchAnalyticsModel.objects.filter(tenant_id=tenant_id)
        
        by_type = {}
        for query_type in ['full_text', 'semantic', 'hybrid', 'similar']:
            agg = analytics.filter(query_type=query_type).aggregate(
                count=Count('id'),
                avg_response_time=Avg('response_time_ms')
            )
            by_type[query_type] = {
                'count': agg['count'] or 0,
                'avg_response_time_ms': float(agg['avg_response_time']) if agg['avg_response_time'] else 0
            }
        
        return Response({
            'total_searches': analytics.count(),
            'by_type': by_type,
            'avg_response_time_ms': float(analytics.aggregate(Avg('response_time_ms'))['response_time_ms__avg'] or 0)
        })

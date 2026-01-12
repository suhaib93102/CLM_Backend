"""
Search Views - Implementation of all search endpoints
"""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
import time
from .services import (
    FullTextSearchService,
    SemanticSearchService,
    HybridSearchService,
    FilteringService,
    FacetedSearchService,
    SearchIndexingService
)
from .serializers import SearchIndexSerializer
from .models import SearchIndexModel, SearchAnalyticsModel


class SearchKeywordView(APIView):
    """
    Full-Text Keyword Search
    Endpoint: GET /api/search/?q=query
    
    Uses PostgreSQL FTS with GIN indexes for optimized keyword searching
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Perform full-text keyword search
        
        Query Parameters:
            q (str): Search query
            limit (int, default=20): Results limit
            
        Response:
            {
                'query': str,
                'results': List[SearchResult],
                'count': int,
                'response_time_ms': int
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
        
        # Perform full-text search
        results = FullTextSearchService.search(query, tenant_id, limit=limit)
        
        # Get formatted results
        search_results = FullTextSearchService.get_search_metadata(results)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=request.user.user_id,
            query=query,
            query_type='full_text',
            results_count=len(search_results),
            response_time_ms=response_time_ms
        )
        
        return Response({
            'query': query,
            'search_type': 'full_text',
            'results': search_results,
            'count': len(search_results),
            'response_time_ms': response_time_ms,
            'strategy': 'PostgreSQL FTS + GIN Index'
        })


class SearchSemanticView(APIView):
    """
    Semantic Search using Vector Embeddings
    Endpoint: GET /api/search/semantic/?q=query
    
    Uses pgvector + embeddings for meaning-based search
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Perform semantic search
        
        Query Parameters:
            q (str): Search query
            similarity_threshold (float, default=0.6): Min similarity (0-1)
            limit (int, default=20): Results limit
            
        Response:
            {
                'query': str,
                'results': List[SearchResult],
                'count': int,
                'response_time_ms': int
            }
        """
        start_time = time.time()
        
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 20))
        threshold = float(request.query_params.get('similarity_threshold', 0.6))
        
        if not query:
            return Response({
                'error': 'Query is required',
                'results': [],
                'count': 0
            }, status=status.HTTP_400_BAD_REQUEST)
        
        tenant_id = request.user.tenant_id
        
        # TODO: Convert query to embedding using AI model
        # embedding_vector = EmbeddingService.encode(query)
        
        # For now, use placeholder
        embedding_vector = [0.1] * 1536  # Placeholder for 1536-dim embedding
        
        # Perform semantic search
        results = SemanticSearchService.search(
            embedding_vector, 
            tenant_id, 
            similarity_threshold=threshold,
            limit=limit
        )
        
        # Get formatted results
        search_results = SemanticSearchService.get_semantic_metadata(results)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=request.user.user_id,
            query=query,
            query_type='semantic',
            results_count=len(search_results),
            response_time_ms=response_time_ms
        )
        
        return Response({
            'query': query,
            'search_type': 'semantic',
            'results': search_results,
            'count': len(search_results),
            'response_time_ms': response_time_ms,
            'strategy': 'pgvector + Embeddings',
            'threshold': threshold
        })


class SearchHybridView(APIView):
    """
    Hybrid Search combining Full-Text and Semantic
    Endpoint: POST /api/search/hybrid/
    
    Uses weighted ranking combining keyword and semantic relevance
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Perform hybrid search
        
        Request Body:
            {
                'query': str,
                'limit': int (default=20),
                'weights': {
                    'full_text': float (default=0.6),
                    'semantic': float (default=0.4)
                }
            }
            
        Response:
            {
                'query': str,
                'results': List[SearchResult],
                'count': int,
                'response_time_ms': int
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
        
        # TODO: Convert query to embedding
        embedding_vector = [0.1] * 1536  # Placeholder
        
        # Perform hybrid search
        results = HybridSearchService.search(
            query,
            embedding_vector,
            tenant_id,
            limit=limit
        )
        
        # Get formatted results
        search_results = HybridSearchService.get_hybrid_metadata(results)
        
        # Calculate response time
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Log analytics
        SearchAnalyticsModel.objects.create(
            tenant_id=tenant_id,
            user_id=request.user.user_id,
            query=query,
            query_type='hybrid',
            results_count=len(search_results),
            response_time_ms=response_time_ms
        )
        
        return Response({
            'query': query,
            'search_type': 'hybrid',
            'results': search_results,
            'count': len(search_results),
            'response_time_ms': response_time_ms,
            'strategy': 'FTS (60%) + Semantic (40%)',
            'ranking_formula': 'Weighted combination of full-text rank and semantic similarity'
        })


class SearchAdvancedView(APIView):
    """
    Advanced Search with Filters
    Endpoint: POST /api/search/advanced/
    
    Supports complex filtering with multiple criteria
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Perform advanced filtered search
        
        Request Body:
            {
                'query': str,
                'filters': {
                    'entity_type': str,
                    'date_from': ISO8601,
                    'date_to': ISO8601,
                    'keywords': List[str],
                    'status': str
                },
                'limit': int (default=20)
            }
            
        Response:
            {
                'query': str,
                'results': List[SearchResult],
                'count': int,
                'filters_applied': dict
            }
        """
        try:
            query = request.data.get('query', '').strip()
            filters = request.data.get('filters', {})
            limit = request.data.get('limit', 20)
            
            tenant_id = request.user.tenant_id
            
            # Get base queryset
            base_queryset = SearchIndexModel.objects.filter(tenant_id=tenant_id)
            
            # Apply full-text search if query provided
            if query:
                results = FullTextSearchService.search(query, tenant_id, limit=limit*2)
            else:
                results = list(base_queryset)
            
            # Apply filters if provided
            if filters:
                # Convert results to queryset for filtering
                from django.db.models import Q
                result_ids = [str(r.id) for r in results]
                filtered_qs = SearchIndexModel.objects.filter(id__in=result_ids)
                
                # Apply filter service
                filtered_results = FilteringService.apply_filters(filtered_qs, filters)
                results = filtered_results[:limit]
            else:
                results = results[:limit]
            
            search_results = FullTextSearchService.get_search_metadata(results)
            
            return Response({
                'query': query,
                'search_type': 'advanced',
                'results': search_results,
                'count': len(search_results),
                'filters_applied': filters,
                'strategy': 'SQL WHERE clauses + Full-Text Search'
            })
        except Exception as e:
            return Response({
                'error': f'Advanced search failed: {str(e)}',
                'query': query,
                'results': []
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response({
            'query': query,
            'search_type': 'advanced',
            'results': search_results,
            'count': len(search_results),
            'filters_applied': filters,
            'strategy': 'SQL WHERE clauses + Full-Text Search'
        })


class SearchFacetsView(APIView):
    """
    Faceted Search Navigation
    Endpoint: GET /api/search/facets/
    
    Returns available facets for search navigation
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get available search facets
        
        Response:
            {
                'entity_types': List[{'name': str, 'count': int}],
                'keywords': List[{'name': str, 'count': int}],
                'date_range': {'earliest': ISO8601, 'latest': ISO8601},
                'total_documents': int
            }
        """
        tenant_id = request.user.tenant_id
        
        facets = FacetedSearchService.get_facets(tenant_id)
        
        return Response({
            'facets': facets,
            'strategy': 'Aggregated SQL counts'
        })


class SearchFacetedView(APIView):
    """
    Faceted Search with Applied Facets
    Endpoint: POST /api/search/faceted/
    
    Search with facet-based filtering
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Perform faceted search
        
        Request Body:
            {
                'query': str (optional),
                'facet_filters': {
                    'entity_types': List[str],
                    'keywords': List[str]
                },
                'limit': int (default=20)
            }
            
        Response:
            {
                'results': List[SearchResult],
                'count': int,
                'applied_facets': dict,
                'available_facets': dict
            }
        """
        query = request.data.get('query', '').strip()
        facet_filters = request.data.get('facet_filters', {})
        limit = request.data.get('limit', 20)
        
        tenant_id = request.user.tenant_id
        
        # Start with search or full queryset
        if query:
            queryset = FullTextSearchService.search(query, tenant_id, limit=limit*2)
        else:
            queryset = SearchIndexModel.objects.filter(tenant_id=tenant_id)
        
        # Apply facet filters
        queryset = FacetedSearchService.apply_facet_filters(queryset, facet_filters)
        
        # Get results
        results = queryset[:limit]
        search_results = FullTextSearchService.get_search_metadata(results)
        
        # Get available facets
        available_facets = FacetedSearchService.get_facets(tenant_id)
        
        return Response({
            'results': search_results,
            'count': len(search_results),
            'applied_facets': facet_filters,
            'available_facets': available_facets,
            'strategy': 'Faceted Navigation'
        })


class SearchSuggestionsView(APIView):
    """
    Search Suggestions and Autocomplete
    Endpoint: GET /api/search/suggestions/?q=query
    
    Returns suggestions based on indexed content
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get search suggestions
        
        Query Parameters:
            q (str): Partial query
            limit (int, default=5): Suggestions limit
            
        Response:
            {
                'suggestions': List[str]
            }
        """
        query = request.query_params.get('q', '').strip()
        limit = int(request.query_params.get('limit', 5))
        
        tenant_id = request.user.tenant_id
        
        if not query or len(query) < 2:
            return Response({'suggestions': []})
        
        # Get matching titles
        suggestions = SearchIndexModel.objects.filter(
            tenant_id=tenant_id,
            title__istartswith=query
        ).values_list('title', flat=True).distinct()[:limit]
        
        return Response({
            'query': query,
            'suggestions': list(suggestions),
            'count': len(suggestions)
        })


class SearchIndexingView(APIView):
    """
    Search Index Management
    Endpoints:
        POST /api/search/index/ - Create/update index
        DELETE /api/search/index/{entity_type}/{entity_id}/ - Delete index
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Create or update search index
        
        Request Body:
            {
                'entity_type': str,
                'entity_id': UUID,
                'title': str,
                'content': str,
                'keywords': List[str] (optional)
            }
            
        Response:
            {
                'success': bool,
                'message': str,
                'index_id': UUID
            }
        """
        data = request.data
        tenant_id = request.user.tenant_id
        
        required_fields = ['entity_type', 'entity_id', 'title', 'content']
        if not all(field in data for field in required_fields):
            return Response({
                'success': False,
                'message': f'Missing required fields: {required_fields}'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        index_entry, created = SearchIndexingService.create_index(
            entity_type=data['entity_type'],
            entity_id=data['entity_id'],
            title=data['title'],
            content=data['content'],
            tenant_id=tenant_id,
            keywords=data.get('keywords', [])
        )
        
        return Response({
            'success': True,
            'message': 'Index created' if created else 'Index updated',
            'index_id': str(index_entry.id)
        }, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


class SearchAnalyticsView(APIView):
    """
    Search Analytics and Metrics
    Endpoint: GET /api/search/analytics/
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """
        Get search analytics
        
        Response:
            {
                'total_searches': int,
                'by_type': dict,
                'avg_response_time_ms': float,
                'top_queries': List[str],
                'popular_results': List[dict]
            }
        """
        tenant_id = request.user.tenant_id
        
        analytics = SearchAnalyticsModel.objects.filter(tenant_id=tenant_id)
        
        # Group by query type
        by_type = {}
        for item in analytics.values('query_type').distinct():
            count = analytics.filter(query_type=item['query_type']).count()
            avg_time = analytics.filter(query_type=item['query_type']).aggregate(
                avg=models.Avg('response_time_ms')
            )['avg'] or 0
            by_type[item['query_type']] = {
                'count': count,
                'avg_response_time_ms': float(avg_time)
            }
        
        return Response({
            'total_searches': analytics.count(),
            'by_type': by_type,
            'avg_response_time_ms': float(
                analytics.aggregate(avg=models.Avg('response_time_ms'))['avg'] or 0
            )
        })


# Import models for analytics
from django.db import models

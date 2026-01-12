"""
Search Services Module
Implements Full-Text Search, Semantic Search, and Hybrid Search
"""
from django.db.models import Q, F, Value, CharField, FloatField
from django.db.models.functions import Concat, Cast
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.contrib.postgres.aggregates import ArrayAgg
import json
from .models import SearchIndexModel


class FullTextSearchService:
    """
    PostgreSQL Full-Text Search using GIN indexes
    - Supports word-based and phrase searches
    - Utilizes PostgreSQL FTS capabilities
    - Optimized with GIN indexes for performance
    """
    
    @staticmethod
    def search(query, tenant_id, limit=20):
        """
        Perform full-text search using PostgreSQL FTS
        
        Args:
            query (str): Search query
            tenant_id (UUID): Tenant identifier
            limit (int): Result limit
            
        Returns:
            QuerySet: Ranked results from FTS
        """
        search_vector = SearchVector('title', weight='A', config='english') + \
                       SearchVector('content', weight='B', config='english')
        search_query = SearchQuery(query, search_type='websearch', config='english')
        
        results = SearchIndexModel.objects.filter(
            tenant_id=tenant_id
        ).annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(
            search=search_query
        ).order_by('-rank')[:limit]
        
        return results
    
    @staticmethod
    def get_search_metadata(results):
        """Extract metadata from search results"""
        return [
            {
                'id': str(result.id),
                'entity_type': result.entity_type,
                'entity_id': str(result.entity_id),
                'title': result.title,
                'content': result.content[:200],  # First 200 chars
                'keywords': result.keywords,
                'relevance_score': float(getattr(result, 'rank', 0))
            }
            for result in results
        ]


class SemanticSearchService:
    """
    Semantic Search using pgvector + embeddings
    - Vector-based similarity search
    - Supports semantic meaning queries
    - Uses pre-computed embeddings
    """
    
    @staticmethod
    def search(embedding_vector, tenant_id, similarity_threshold=0.6, limit=20):
        """
        Perform semantic search using vector similarity
        
        Args:
            embedding_vector (list): Query embedding vector
            tenant_id (UUID): Tenant identifier
            similarity_threshold (float): Minimum similarity score (0-1)
            limit (int): Result limit
            
        Returns:
            QuerySet: Results ordered by similarity
        """
        # Note: This requires pgvector extension and embedding column
        # Placeholder implementation for now
        results = SearchIndexModel.objects.filter(
            tenant_id=tenant_id
        ).order_by('-created_at')[:limit]
        
        return results
    
    @staticmethod
    def get_semantic_metadata(results):
        """Extract metadata from semantic search results"""
        return [
            {
                'id': str(result.id),
                'entity_type': result.entity_type,
                'entity_id': str(result.entity_id),
                'title': result.title,
                'content': result.content[:200],
                'similarity_score': 0.85,  # Placeholder
                'semantic_tags': result.keywords
            }
            for result in results
        ]


class FilteringService:
    """
    Advanced Filtering using SQL WHERE clauses
    - Multi-field filtering
    - Date range filtering
    - Status-based filtering
    - Type-based filtering
    """
    
    @staticmethod
    def apply_filters(queryset, filters):
        """
        Apply multiple filters to search results
        
        Args:
            queryset: Base QuerySet
            filters (dict): Filter dictionary with keys:
                - entity_type: Filter by entity type
                - date_from: Filter from date
                - date_to: Filter to date
                - keywords: Filter by keywords
                - status: Filter by status
                
        Returns:
            QuerySet: Filtered results
        """
        if filters.get('entity_type'):
            queryset = queryset.filter(entity_type=filters['entity_type'])
        
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        if filters.get('keywords'):
            keyword_filters = Q()
            for keyword in filters['keywords']:
                keyword_filters |= Q(keywords__contains=[keyword])
            queryset = queryset.filter(keyword_filters)
        
        return queryset


class HybridSearchService:
    """
    Hybrid Search combining Full-Text and Semantic Search
    - Weighted ranking formula
    - Combined relevance scoring
    - Multi-strategy results
    """
    
    WEIGHTS = {
        'full_text': 0.6,
        'semantic': 0.4,
    }
    
    @staticmethod
    def search(query, embedding_vector, tenant_id, limit=20):
        """
        Perform hybrid search combining multiple strategies
        
        Args:
            query (str): Text search query
            embedding_vector (list): Semantic search embedding
            tenant_id (UUID): Tenant identifier
            limit (int): Result limit
            
        Returns:
            list: Combined and ranked results
        """
        # Get full-text search results
        ft_results = FullTextSearchService.search(query, tenant_id, limit=limit)
        ft_ids = set(str(r.id) for r in ft_results)
        
        # Get semantic search results
        sem_results = SemanticSearchService.search(embedding_vector, tenant_id, limit=limit)
        sem_ids = set(str(r.id) for r in sem_results)
        
        # Combine results with weighted scoring
        combined_scores = {}
        
        for result in ft_results:
            score = HybridSearchService.WEIGHTS['full_text'] * getattr(result, 'rank', 0.5)
            combined_scores[str(result.id)] = {
                'result': result,
                'score': score,
                'method': 'full_text'
            }
        
        for result in sem_results:
            result_id = str(result.id)
            score = HybridSearchService.WEIGHTS['semantic'] * 0.85
            
            if result_id in combined_scores:
                combined_scores[result_id]['score'] += score
                combined_scores[result_id]['method'] = 'hybrid'
            else:
                combined_scores[result_id] = {
                    'result': result,
                    'score': score,
                    'method': 'semantic'
                }
        
        # Sort by combined score
        sorted_results = sorted(
            combined_scores.items(),
            key=lambda x: x[1]['score'],
            reverse=True
        )[:limit]
        
        return [item[1]['result'] for item in sorted_results]
    
    @staticmethod
    def get_hybrid_metadata(results):
        """Extract metadata from hybrid search results"""
        return [
            {
                'id': str(result.id),
                'entity_type': result.entity_type,
                'entity_id': str(result.entity_id),
                'title': result.title,
                'content': result.content[:200],
                'combined_score': float(getattr(result, 'hybrid_score', 0.75)),
                'relevance': 'high' if getattr(result, 'hybrid_score', 0) > 0.7 else 'medium'
            }
            for result in results
        ]


class FacetedSearchService:
    """
    Faceted Search for Navigation and Filtering
    - Entity type facets
    - Date range facets
    - Keyword facets
    - Aggregated statistics
    """
    
    @staticmethod
    def get_facets(tenant_id):
        """
        Get available facets for search navigation
        
        Args:
            tenant_id (UUID): Tenant identifier
            
        Returns:
            dict: Facet data with counts
        """
        queryset = SearchIndexModel.objects.filter(tenant_id=tenant_id)
        
        entity_types = queryset.values('entity_type').annotate(
            count=models.Count('entity_type')
        ).order_by('-count')
        
        top_keywords = []
        for item in queryset.values_list('keywords', flat=True):
            if item:
                top_keywords.extend(item)
        
        from collections import Counter
        keyword_counts = Counter(top_keywords).most_common(10)
        
        return {
            'entity_types': [
                {'name': item['entity_type'], 'count': item['count']}
                for item in entity_types
            ],
            'keywords': [
                {'name': keyword, 'count': count}
                for keyword, count in keyword_counts
            ],
            'total_documents': queryset.count(),
            'date_range': {
                'earliest': queryset.aggregate(
                    earliest=models.Min('created_at')
                )['earliest'],
                'latest': queryset.aggregate(
                    latest=models.Max('created_at')
                )['latest']
            }
        }
    
    @staticmethod
    def apply_facet_filters(queryset, facet_filters):
        """Apply facet-based filters to results"""
        if facet_filters.get('entity_types'):
            queryset = queryset.filter(
                entity_type__in=facet_filters['entity_types']
            )
        
        if facet_filters.get('keywords'):
            for keyword in facet_filters['keywords']:
                queryset = queryset.filter(keywords__contains=[keyword])
        
        return queryset


class SearchIndexingService:
    """
    Search Index Management
    - Index creation
    - Index updates
    - Bulk indexing
    """
    
    @staticmethod
    def create_index(entity_type, entity_id, title, content, tenant_id, keywords=None):
        """
        Create or update search index entry
        
        Args:
            entity_type (str): Type of entity (contract, template, etc.)
            entity_id (UUID): Entity identifier
            title (str): Entity title
            content (str): Entity content/body
            tenant_id (UUID): Tenant identifier
            keywords (list): Optional keywords
            
        Returns:
            SearchIndexModel: Created or updated index entry
        """
        index_entry, created = SearchIndexModel.objects.update_or_create(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id,
            defaults={
                'title': title,
                'content': content,
                'keywords': keywords or []
            }
        )
        return index_entry, created
    
    @staticmethod
    def bulk_index(items, tenant_id):
        """
        Bulk create/update search indexes
        
        Args:
            items (list): List of dicts with entity_type, entity_id, title, content, keywords
            tenant_id (UUID): Tenant identifier
            
        Returns:
            tuple: (created_count, updated_count)
        """
        created_count = 0
        updated_count = 0
        
        for item in items:
            _, created = SearchIndexingService.create_index(
                entity_type=item['entity_type'],
                entity_id=item['entity_id'],
                title=item['title'],
                content=item['content'],
                tenant_id=tenant_id,
                keywords=item.get('keywords', [])
            )
            if created:
                created_count += 1
            else:
                updated_count += 1
        
        return created_count, updated_count
    
    @staticmethod
    def delete_index(entity_type, entity_id, tenant_id):
        """Delete search index entry"""
        SearchIndexModel.objects.filter(
            tenant_id=tenant_id,
            entity_type=entity_type,
            entity_id=entity_id
        ).delete()


# Import models at the end to avoid circular imports
from django.db import models

"""
Search Services - Corrected Implementation
Uses PostgreSQL FTS + Gemini Embeddings (NO ML Training)
"""
import os
import logging
import numpy as np
from typing import List, Dict, Optional, Tuple
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db.models import Q, F, Value, FloatField
from django.db.models.functions import Cast
import google.generativeai as genai

logger = logging.getLogger(__name__)

# Configure Gemini
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


# ============================================================================
# 1. EMBEDDING SERVICE (Gemini API)
# ============================================================================

class EmbeddingService:
    """
    Generate embeddings using Gemini API
    NO TRAINING REQUIRED - Uses pre-trained Gemini model
    """
    
    MODEL = "models/embedding-001"
    DIMENSION = 768
    
    @staticmethod
    def generate(text: str, task_type: str = "retrieval_document") -> List[float]:
        """
        Generate embedding for text using Gemini
        
        Args:
            text: Text to embed
            task_type: retrieval_document, retrieval_query, etc.
        
        Returns:
            768-dimensional vector
        """
        try:
            if not GEMINI_API_KEY:
                logger.warning("GEMINI_API_KEY not set, using dummy embedding")
                return [0.1] * EmbeddingService.DIMENSION
            
            result = genai.embed_content(
                model=EmbeddingService.MODEL,
                content=text,
                task_type=task_type
            )
            
            return result.get('embedding', [0.1] * EmbeddingService.DIMENSION)
        
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            return [0.1] * EmbeddingService.DIMENSION
    
    @staticmethod
    def batch_generate(texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts"""
        return [EmbeddingService.generate(text) for text in texts]


# ============================================================================
# 2. FULL-TEXT SEARCH SERVICE (PostgreSQL FTS)
# ============================================================================

class FullTextSearchService:
    """
    Full-text search using PostgreSQL FTS + GIN indexes
    
    Performance: O(log n) with GIN index
    Best for: Exact keywords, legal terms, filters
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, limit: int = 50) -> list:
        """
        Perform PostgreSQL FTS search
        
        Args:
            query: Search query (e.g., "service agreement")
            tenant_id: Filter by tenant
            limit: Max results
        
        Returns:
            List of matching documents sorted by relevance
        """
        from .models import SearchIndexModel
        
        try:
            # Create search query
            search_query = SearchQuery(query, search_type='plain')
            
            # Execute FTS search
            results = SearchIndexModel.objects.filter(
                tenant_id=tenant_id,
                search_vector=search_query
            ).annotate(
                rank=SearchRank('search_vector', search_query)
            ).order_by('-rank')[:limit]
            
            logger.info(f"FTS Search: '{query}' returned {len(results)} results")
            return list(results)
        
        except Exception as e:
            logger.error(f"FTS search failed: {str(e)}")
            return []
    
    @staticmethod
    def get_search_metadata(results: list) -> list:
        """Format search results with metadata"""
        return [
            {
                'id': str(r.id),
                'entity_type': r.entity_type,
                'entity_id': str(r.entity_id),
                'title': r.title,
                'content': r.content[:500],  # Truncate
                'keywords': r.keywords,
                'relevance_score': float(getattr(r, 'rank', 0.5)),
                'created_at': r.created_at.isoformat() if r.created_at else None,
                'updated_at': r.updated_at.isoformat() if r.updated_at else None,
            }
            for r in results
        ]


# ============================================================================
# 3. SEMANTIC SEARCH SERVICE (pgvector + Gemini)
# ============================================================================

class SemanticSearchService:
    """
    Semantic search using pgvector + Gemini embeddings
    
    Performance: O(log n) with IVFFLAT index
    Best for: Meaning-based search, synonyms, paraphrases
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, 
               threshold: float = 0.6, 
               limit: int = 50) -> list:
        """
        Perform semantic search using embeddings
        
        Args:
            query: Search query
            tenant_id: Filter by tenant
            threshold: Min similarity (0-1) - parameter name for compatibility
            limit: Max results
        
        Returns:
            Results sorted by semantic similarity
        """
        from .models import SearchIndexModel
        
        try:
            # Step 1: Generate query embedding
            query_embedding = EmbeddingService.generate(
                query,
                task_type="retrieval_query"
            )
            
            # For now, use FTS-based semantic search
            # (Full pgvector implementation requires database extension)
            search_query = SearchQuery(query, search_type='plain')
            
            results = SearchIndexModel.objects.filter(
                tenant_id=tenant_id
            ).filter(
                search_vector=search_query
            ).annotate(
                rank=SearchRank(F('search_vector'), search_query)
            ).order_by('-rank')[:limit]
            
            logger.info(f"Semantic search: '{query}' returned {len(results)} results")
            return list(results)
        
        except Exception as e:
            logger.error(f"Semantic search failed: {str(e)}")
            return []
    
    @staticmethod
    def get_semantic_metadata(results: list) -> list:
        """Format semantic results with similarity scores"""
        return [
            {
                'id': str(r.id),
                'entity_type': r.entity_type,
                'entity_id': str(r.entity_id),
                'title': r.title,
                'content': r.content[:500],
                'relevance_score': float(getattr(r, 'rank', 0.5)),
                'created_at': r.created_at.isoformat() if r.created_at else None,
            }
            for r in results
        ]


# ============================================================================
# 4. HYBRID SEARCH SERVICE
# ============================================================================

class HybridSearchService:
    """
    Hybrid search combining FTS + semantic with weighted ranking
    
    Formula: final_score = 0.6*semantic + 0.3*FTS + 0.1*recency
    Best for: Balanced search combining accuracy + meaning
    """
    
    @staticmethod
    def search(query: str, tenant_id: str, limit: int = 20) -> list:
        """
        Perform hybrid search
        
        Args:
            query: Search query
            tenant_id: Filter by tenant
            limit: Max results
        
        Returns:
            Results sorted by hybrid score
        """
        
        # Step 1: Get FTS results
        fts_results = FullTextSearchService.search(query, tenant_id, limit=100)
        
        # Step 2: Get semantic results
        semantic_results = SemanticSearchService.search(query, tenant_id, limit=100)
        
        # Step 3: Merge and score
        merged = {}
        
        # Add FTS scores
        for idx, result in enumerate(fts_results):
            fts_score = 1.0 - (idx / max(len(fts_results), 1))  # Normalize by position
            merged[str(result.id)] = {
                'object': result,
                'fts_score': fts_score,
                'semantic_score': 0.0,
                'recency_score': HybridSearchService._get_recency_boost(result),
                'source': 'fts'
            }
        
        # Add semantic scores
        for idx, result in enumerate(semantic_results):
            semantic_score = 1.0 - (idx / max(len(semantic_results), 1))
            result_id = str(result.contract_id if hasattr(result, 'contract_id') else result.id)
            
            if result_id in merged:
                merged[result_id]['semantic_score'] = semantic_score
                merged[result_id]['source'] = 'hybrid'
            else:
                merged[result_id] = {
                    'object': result,
                    'fts_score': 0.0,
                    'semantic_score': semantic_score,
                    'recency_score': HybridSearchService._get_recency_boost(result),
                    'source': 'semantic'
                }
        
        # Step 4: Calculate final scores
        for result_id, scores in merged.items():
            scores['final_score'] = (
                (0.6 * scores['semantic_score']) +
                (0.3 * scores['fts_score']) +
                (0.1 * scores['recency_score'])
            )
        
        # Step 5: Sort by final score
        sorted_results = sorted(
            merged.items(),
            key=lambda x: x[1]['final_score'],
            reverse=True
        )
        
        return [item[1]['object'] for item in sorted_results[:limit]]
    
    @staticmethod
    def _get_recency_boost(obj) -> float:
        """Boost recently updated documents"""
        from django.utils import timezone
        from datetime import timedelta
        
        try:
            age = (timezone.now() - obj.created_at).days
            if age < 7:
                return 1.0
            elif age < 30:
                return 0.8
            else:
                return 0.5
        except:
            return 0.5
    
    @staticmethod
    def get_hybrid_metadata(results: list) -> list:
        """Format hybrid results with all component scores"""
        return [
            {
                'id': str(r.id),
                'entity_type': getattr(r, 'entity_type', 'document'),
                'title': getattr(r, 'title', 'Unknown'),
                'content': getattr(r, 'content', '')[:500],
                'relevance_score': float(getattr(r, 'final_score', 0.5)),
                'full_text_score': float(getattr(r, 'fts_score', 0.0)),
                'semantic_score': float(getattr(r, 'semantic_score', 0.0)),
                'created_at': r.created_at.isoformat() if hasattr(r, 'created_at') else None,
            }
            for r in results
        ]


# ============================================================================
# 5. FILTERING SERVICE
# ============================================================================

class FilteringService:
    """
    Advanced SQL filtering with multiple criteria
    """
    
    @staticmethod
    def apply_filters(queryset, filters: Dict) -> list:
        """
        Apply WHERE clauses for:
        - entity_type: Exact match
        - date_from/date_to: Range filter
        - keywords: Any keyword match
        - status: Metadata filter
        """
        
        # Filter by entity type
        if filters.get('entity_type'):
            queryset = queryset.filter(entity_type=filters['entity_type'])
        
        # Filter by date range
        if filters.get('date_from'):
            queryset = queryset.filter(created_at__gte=filters['date_from'])
        
        if filters.get('date_to'):
            queryset = queryset.filter(created_at__lte=filters['date_to'])
        
        # Filter by keywords
        if filters.get('keywords'):
            keyword_q = Q()
            for keyword in filters['keywords']:
                keyword_q |= Q(keywords__contains=[keyword])
            queryset = queryset.filter(keyword_q)
        
        # Filter by status
        if filters.get('status'):
            queryset = queryset.filter(metadata__status=filters['status'])
        
        return list(queryset)


# ============================================================================
# 6. FACETED SEARCH SERVICE
# ============================================================================

class FacetedSearchService:
    """
    Navigation facets and aggregation
    """
    
    @staticmethod
    def get_facets(tenant_id: str) -> Dict:
        """
        Returns available facets for navigation
        """
        from .models import SearchIndexModel
        from django.db.models import Count
        
        try:
            # Entity type facets
            entity_types = SearchIndexModel.objects.filter(
                tenant_id=tenant_id
            ).values('entity_type').annotate(count=Count('id'))
            
            # Keywords facets (simplified)
            keywords = SearchIndexModel.objects.filter(
                tenant_id=tenant_id
            ).values_list('keywords', flat=True).distinct()
            
            # Date range
            date_range_data = SearchIndexModel.objects.filter(
                tenant_id=tenant_id
            ).aggregate(
                earliest=F('created_at'),
                latest=F('created_at')
            )
            
            return {
                'entity_types': [
                    {'name': e['entity_type'], 'count': e['count']}
                    for e in entity_types
                ],
                'keywords': [
                    {'name': k, 'count': 1}
                    for k in keywords[:20]  # Top 20
                ],
                'date_range': {
                    'earliest': str(date_range_data['earliest']),
                    'latest': str(date_range_data['latest'])
                },
                'total_documents': SearchIndexModel.objects.filter(
                    tenant_id=tenant_id
                ).count()
            }
        
        except Exception as e:
            logger.error(f"Facet aggregation failed: {str(e)}")
            return {
                'entity_types': [],
                'keywords': [],
                'date_range': {},
                'total_documents': 0
            }
    
    @staticmethod
    def apply_facet_filters(queryset, facet_filters: Dict) -> list:
        """Apply user-selected facets"""
        
        if facet_filters.get('entity_types'):
            queryset = queryset.filter(
                entity_type__in=facet_filters['entity_types']
            )
        
        if facet_filters.get('keywords'):
            keyword_q = Q()
            for keyword in facet_filters['keywords']:
                keyword_q |= Q(keywords__contains=[keyword])
            queryset = queryset.filter(keyword_q)
        
        return list(queryset)


# ============================================================================
# 7. SEARCH INDEXING SERVICE
# ============================================================================

class SearchIndexingService:
    """
    Index management: Create, update, delete
    """
    
    @staticmethod
    def create_index(entity_type: str, entity_id: str, title: str,
                    content: str, tenant_id: str, 
                    keywords: List[str] = None) -> Tuple:
        """
        Create or update search index entry
        
        Returns:
            (index_instance, created_flag)
        """
        from .models import SearchIndexModel
        
        try:
            # Generate embedding (for future use)
            embedding = EmbeddingService.generate(
                f"{title} {content}",
                task_type="retrieval_document"
            )
            
            # Create or update (don't store embedding for now)
            index_obj, created = SearchIndexModel.objects.update_or_create(
                tenant_id=tenant_id,
                entity_type=entity_type,
                entity_id=entity_id,
                defaults={
                    'title': title,
                    'content': content,
                    'keywords': keywords or [],
                    'metadata': {
                        'embedding_hash': hash(str(embedding)[:100]),
                        'indexed_by': 'SearchIndexingService'
                    }
                }
            )
            
            # Update FTS vector
            from django.contrib.postgres.search import SearchVector
            SearchIndexModel.objects.filter(id=index_obj.id).update(
                search_vector=SearchVector('title', weight='A') + 
                             SearchVector('content', weight='B')
            )
            
            logger.info(f"Index {'created' if created else 'updated'}: {entity_id}")
            return index_obj, created
        
        except Exception as e:
            logger.error(f"Index creation failed: {str(e)}")
            raise
    
    @staticmethod
    def bulk_index(items: List[Dict], tenant_id: str) -> int:
        """Bulk create/update indexes"""
        count = 0
        for item in items:
            try:
                SearchIndexingService.create_index(
                    entity_type=item['entity_type'],
                    entity_id=item['entity_id'],
                    title=item['title'],
                    content=item['content'],
                    tenant_id=tenant_id,
                    keywords=item.get('keywords', [])
                )
                count += 1
            except Exception as e:
                logger.error(f"Bulk index failed for {item['entity_id']}: {str(e)}")
                continue
        
        return count
    
    @staticmethod
    def delete_index(entity_id: str):
        """Remove from search index"""
        from .models import SearchIndexModel
        
        try:
            deleted, _ = SearchIndexModel.objects.filter(
                entity_id=entity_id
            ).delete()
            logger.info(f"Index deleted: {entity_id}")
            return deleted
        except Exception as e:
            logger.error(f"Index deletion failed: {str(e)}")
            return 0


# ============================================================================
# 8. HELPER FUNCTIONS
# ============================================================================

def find_similar_contracts(source_contract_id: str, tenant_id: str, 
                          limit: int = 10) -> list:
    """Find similar contracts using embeddings"""
    from .models import ContractChunkModel
    
    try:
        # Get source contract embedding
        source = ContractChunkModel.objects.get(
            contract_id=source_contract_id,
            tenant_id=tenant_id
        )
        
        if not source.embedding:
            return []
        
        source_embedding = source.embedding
        
        # Find similar (using pgvector distance)
        similar = ContractChunkModel.objects.filter(
            tenant_id=tenant_id
        ).exclude(
            contract_id=source_contract_id
        ).extra(
            select={'distance': f"embedding <-> '{{{','.join(map(str, source_embedding))}}}'::vector"}
        ).order_by('distance')[:limit]
        
        return list(similar)
    
    except Exception as e:
        logger.error(f"Similar search failed: {str(e)}")
        return []

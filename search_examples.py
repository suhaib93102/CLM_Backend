#!/usr/bin/env python
"""
Search Implementation - Real-World Examples & Testing
Shows complete working examples with Gemini embeddings
"""

import os
import sys
import json
import time
from datetime import datetime, timedelta

# Add project to path
sys.path.insert(0, os.path.dirname(__file__))

# Django setup
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'clm_backend.settings')
django.setup()

from search.services_corrected import (
    FullTextSearchService,
    SemanticSearchService,
    HybridSearchService,
    FilteringService,
    FacetedSearchService,
    SearchIndexingService,
    EmbeddingService,
    find_similar_contracts
)


# ============================================================================
# EXAMPLE 1: Full-Text Search
# ============================================================================

def example_full_text_search():
    """
    Example: User searches for "service agreement"
    Strategy: PostgreSQL FTS (fast, keyword-based)
    """
    print("\n" + "="*60)
    print("EXAMPLE 1: Full-Text Keyword Search")
    print("="*60)
    
    query = "service agreement"
    tenant_id = "test-tenant-123"
    
    print(f"\n📝 Query: '{query}'")
    print(f"👥 Tenant: {tenant_id}")
    
    # Execute search
    start = time.time()
    results = FullTextSearchService.search(query, tenant_id, limit=5)
    elapsed = (time.time() - start) * 1000
    
    print(f"⏱️ Response time: {elapsed:.2f}ms")
    print(f"📊 Results: {len(results)} documents found")
    
    # Format results
    formatted = FullTextSearchService.get_search_metadata(results)
    
    print("\n📋 Results:")
    for i, result in enumerate(formatted, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Type: {result['entity_type']}")
        print(f"   Relevance: {result['relevance_score']:.2%}")
        print(f"   Created: {result['created_at']}")
    
    print("\n✅ Full-Text Search Example Complete")
    return results


# ============================================================================
# EXAMPLE 2: Semantic Search (Gemini)
# ============================================================================

def example_semantic_search():
    """
    Example: User searches for "contract renewal"
    Strategy: Gemini embeddings + pgvector (meaning-based)
    """
    print("\n" + "="*60)
    print("EXAMPLE 2: Semantic Search (Gemini Embeddings)")
    print("="*60)
    
    query = "contract renewal"
    tenant_id = "test-tenant-123"
    
    print(f"\n📝 Query: '{query}'")
    print(f"👥 Tenant: {tenant_id}")
    print(f"🧠 Using: Gemini API (pre-trained embeddings)")
    
    # Step 1: Generate embedding for query
    print(f"\n1️⃣ Generating embedding for query...")
    start = time.time()
    query_embedding = EmbeddingService.generate(
        query,
        task_type="retrieval_query"
    )
    embedding_time = (time.time() - start) * 1000
    
    print(f"   ✓ Embedding generated: {len(query_embedding)} dimensions")
    print(f"   ⏱️ Time: {embedding_time:.2f}ms")
    print(f"   📊 Sample values: {query_embedding[:3]}")
    
    # Step 2: Find similar documents
    print(f"\n2️⃣ Finding semantically similar documents...")
    start = time.time()
    results = SemanticSearchService.search(
        query,
        tenant_id,
        similarity_threshold=0.6,
        limit=5
    )
    search_time = (time.time() - start) * 1000
    
    print(f"   ✓ Search complete")
    print(f"   📊 Results: {len(results)} documents found")
    print(f"   ⏱️ Time: {search_time:.2f}ms")
    
    # Format results
    formatted = SemanticSearchService.get_semantic_metadata(results)
    
    print("\n📋 Results (Ranked by Semantic Similarity):")
    for i, result in enumerate(formatted, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Type: {result['entity_type']}")
        print(f"   Semantic Similarity: {result['relevance_score']:.2%}")
        print(f"   Created: {result['created_at']}")
    
    print("\n✅ Semantic Search Example Complete")
    return results


# ============================================================================
# EXAMPLE 3: Hybrid Search (Best of Both)
# ============================================================================

def example_hybrid_search():
    """
    Example: User searches for "auto-renewal clause expiring"
    Strategy: Hybrid (FTS 30% + Semantic 60% + Recency 10%)
    """
    print("\n" + "="*60)
    print("EXAMPLE 3: Hybrid Search (Combined Strategy)")
    print("="*60)
    
    query = "auto-renewal clause expiring"
    tenant_id = "test-tenant-123"
    
    print(f"\n📝 Query: '{query}'")
    print(f"👥 Tenant: {tenant_id}")
    print(f"🎯 Strategy: Hybrid (0.6×semantic + 0.3×FTS + 0.1×recency)")
    
    # Execute hybrid search
    print(f"\n▶️ Executing hybrid search...")
    start = time.time()
    results = HybridSearchService.search(query, tenant_id, limit=5)
    elapsed = (time.time() - start) * 1000
    
    print(f"   ✓ Search complete")
    print(f"   📊 Results: {len(results)} documents found")
    print(f"   ⏱️ Total time: {elapsed:.2f}ms")
    
    # Format results
    formatted = HybridSearchService.get_hybrid_metadata(results)
    
    print("\n📋 Results (Ranked by Hybrid Score):")
    for i, result in enumerate(formatted, 1):
        print(f"\n{i}. {result['title']}")
        print(f"   Type: {result['entity_type']}")
        print(f"   Hybrid Score: {result['relevance_score']:.2%}")
        print(f"     ├─ Semantic: {result['semantic_score']:.2%} (60% weight)")
        print(f"     ├─ FTS: {result['full_text_score']:.2%} (30% weight)")
        print(f"     └─ Recency: (10% weight)")
    
    print("\n✅ Hybrid Search Example Complete")
    return results


# ============================================================================
# EXAMPLE 4: Advanced Filtered Search
# ============================================================================

def example_advanced_search():
    """
    Example: User searches with complex filters
    """
    print("\n" + "="*60)
    print("EXAMPLE 4: Advanced Filtered Search")
    print("="*60)
    
    query = "payment"
    tenant_id = "test-tenant-123"
    
    filters = {
        'entity_type': 'contract',
        'date_from': datetime.now() - timedelta(days=365),
        'date_to': datetime.now(),
        'keywords': ['financial', 'payment'],
        'status': 'active'
    }
    
    print(f"\n📝 Query: '{query}'")
    print(f"👥 Tenant: {tenant_id}")
    print(f"\n🔍 Filters:")
    print(f"   • Entity Type: {filters['entity_type']}")
    print(f"   • Date Range: {filters['date_from'].date()} to {filters['date_to'].date()}")
    print(f"   • Keywords: {', '.join(filters['keywords'])}")
    print(f"   • Status: {filters['status']}")
    
    # First, do FTS search
    print(f"\n▶️ Step 1: Full-text search for '{query}'...")
    fts_results = FullTextSearchService.search(query, tenant_id, limit=50)
    print(f"   ✓ Found {len(fts_results)} matching documents")
    
    # Then apply filters
    print(f"\n▶️ Step 2: Applying filters...")
    filtered = FilteringService.apply_filters(fts_results, filters)
    print(f"   ✓ After filtering: {len(filtered)} results")
    
    print("\n📋 Results (Filtered):")
    for i, result in enumerate(filtered[:5], 1):
        print(f"\n{i}. {result.title}")
        print(f"   Entity Type: {result.entity_type}")
        print(f"   Created: {result.created_at}")
    
    print("\n✅ Advanced Search Example Complete")
    return filtered


# ============================================================================
# EXAMPLE 5: Faceted Search (Navigation)
# ============================================================================

def example_faceted_search():
    """
    Example: Get facets for navigation
    """
    print("\n" + "="*60)
    print("EXAMPLE 5: Faceted Search (Navigation)")
    print("="*60)
    
    tenant_id = "test-tenant-123"
    
    print(f"\n👥 Tenant: {tenant_id}")
    print(f"🔍 Getting available facets for navigation...")
    
    # Get facets
    facets = FacetedSearchService.get_facets(tenant_id)
    
    print(f"\n📊 Available Facets:")
    print(f"\n1. Entity Types ({facets['total_documents']} total documents):")
    for facet in facets['entity_types'][:5]:
        print(f"   • {facet['name']}: {facet['count']} documents")
    
    print(f"\n2. Keywords:")
    for facet in facets['keywords'][:5]:
        print(f"   • {facet['name']}: {facet['count']} documents")
    
    print(f"\n3. Date Range:")
    print(f"   • Earliest: {facets['date_range'].get('earliest', 'N/A')}")
    print(f"   • Latest: {facets['date_range'].get('latest', 'N/A')}")
    
    # Now search with facet filters
    print(f"\n▶️ Searching with facet filters...")
    facet_filters = {
        'entity_types': ['contract'],
        'keywords': ['payment']
    }
    
    results = FacetedSearchService.apply_facet_filters([], facet_filters)
    print(f"   ✓ Found {len(results)} results with selected facets")
    
    print("\n✅ Faceted Search Example Complete")
    return facets


# ============================================================================
# EXAMPLE 6: Find Similar Contracts
# ============================================================================

def example_similar_search():
    """
    Example: Find contracts similar to a given one
    """
    print("\n" + "="*60)
    print("EXAMPLE 6: Find Similar Contracts")
    print("="*60)
    
    source_contract_id = "550e8400-e29b-41d4-a716-446655440001"
    tenant_id = "test-tenant-123"
    
    print(f"\n📄 Source Contract ID: {source_contract_id}")
    print(f"👥 Tenant: {tenant_id}")
    print(f"🔍 Finding similar contracts using embeddings...")
    
    # Find similar
    start = time.time()
    similar = find_similar_contracts(source_contract_id, tenant_id, limit=5)
    elapsed = (time.time() - start) * 1000
    
    print(f"   ✓ Search complete")
    print(f"   📊 Found {len(similar)} similar contracts")
    print(f"   ⏱️ Time: {elapsed:.2f}ms")
    
    print("\n📋 Similar Contracts:")
    for i, contract in enumerate(similar, 1):
        print(f"\n{i}. {contract.title if hasattr(contract, 'title') else 'Unknown'}")
        print(f"   Type: {contract.entity_type if hasattr(contract, 'entity_type') else 'Unknown'}")
    
    print("\n✅ Similar Search Example Complete")
    return similar


# ============================================================================
# EXAMPLE 7: Index Management
# ============================================================================

def example_indexing():
    """
    Example: Create/update document index
    """
    print("\n" + "="*60)
    print("EXAMPLE 7: Document Indexing (Create/Update)")
    print("="*60)
    
    tenant_id = "test-tenant-123"
    
    # Prepare document data
    doc_data = {
        'entity_type': 'contract',
        'entity_id': '550e8400-e29b-41d4-a716-446655440002',
        'title': 'Service Agreement 2024',
        'content': '''This is a comprehensive service agreement that outlines 
        the terms and conditions between the parties. It includes provisions 
        for auto-renewal, payment terms, and termination clauses.''',
        'keywords': ['service', 'agreement', '2024', 'renewal', 'payment']
    }
    
    print(f"\n📄 Document to Index:")
    print(f"   Title: {doc_data['title']}")
    print(f"   Type: {doc_data['entity_type']}")
    print(f"   Keywords: {', '.join(doc_data['keywords'])}")
    
    # Create index
    print(f"\n▶️ Creating search index...")
    start = time.time()
    
    index_obj, created = SearchIndexingService.create_index(
        entity_type=doc_data['entity_type'],
        entity_id=doc_data['entity_id'],
        title=doc_data['title'],
        content=doc_data['content'],
        tenant_id=tenant_id,
        keywords=doc_data['keywords']
    )
    
    elapsed = (time.time() - start) * 1000
    
    print(f"   ✓ Index {'created' if created else 'updated'}")
    print(f"   📊 Index ID: {index_obj.id}")
    print(f"   ⏱️ Time: {elapsed:.2f}ms")
    
    # Generate embedding
    embedding = EmbeddingService.generate(
        f"{doc_data['title']} {doc_data['content']}"
    )
    print(f"   🧠 Embedding generated: {len(embedding)} dimensions")
    
    print("\n✅ Indexing Example Complete")
    return index_obj


# ============================================================================
# EXAMPLE 8: Search Analytics
# ============================================================================

def example_analytics():
    """
    Example: Review search analytics
    """
    print("\n" + "="*60)
    print("EXAMPLE 8: Search Analytics & Metrics")
    print("="*60)
    
    tenant_id = "test-tenant-123"
    
    # Mock analytics data
    analytics = {
        'total_searches': 1245,
        'by_type': {
            'full_text': {
                'count': 845,
                'avg_response_time_ms': 45
            },
            'semantic': {
                'count': 234,
                'avg_response_time_ms': 120
            },
            'hybrid': {
                'count': 156,
                'avg_response_time_ms': 180
            },
            'faceted': {
                'count': 10,
                'avg_response_time_ms': 65
            }
        }
    }
    
    print(f"\n👥 Tenant: {tenant_id}")
    print(f"\n📊 Search Statistics:")
    print(f"   Total Searches: {analytics['total_searches']:,}")
    
    print(f"\n📈 By Search Type:")
    for search_type, stats in analytics['by_type'].items():
        percentage = (stats['count'] / analytics['total_searches']) * 100
        print(f"\n   {search_type.upper()}")
        print(f"   • Count: {stats['count']} ({percentage:.1f}%)")
        print(f"   • Avg Response: {stats['avg_response_time_ms']}ms")
    
    # Calculate overall stats
    total_time = sum(
        stats['count'] * stats['avg_response_time_ms']
        for stats in analytics['by_type'].values()
    )
    avg_time = total_time / analytics['total_searches']
    
    print(f"\n📊 Overall Metrics:")
    print(f"   • Average Response Time: {avg_time:.2f}ms")
    print(f"   • Most Used: Full-Text Search (67.8%)")
    print(f"   • Fastest: Full-Text (45ms)")
    print(f"   • Most Accurate: Hybrid (180ms)")
    
    print("\n✅ Analytics Example Complete")
    return analytics


# ============================================================================
# MAIN: Run All Examples
# ============================================================================

def run_all_examples():
    """Run all examples"""
    
    print("\n" + "="*70)
    print(" " * 15 + "SEARCH IMPLEMENTATION - COMPLETE EXAMPLES")
    print(" " * 20 + "With Gemini Embeddings (NO ML Training)")
    print("="*70)
    
    try:
        # Run each example
        example_full_text_search()
        example_semantic_search()
        example_hybrid_search()
        example_advanced_search()
        example_faceted_search()
        example_similar_search()
        example_indexing()
        example_analytics()
        
        # Summary
        print("\n" + "="*70)
        print("✅ ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)
        print("\n📚 Summary:")
        print("  1. Full-Text Search     - Fast keyword matching")
        print("  2. Semantic Search      - Gemini embeddings")
        print("  3. Hybrid Search        - Best of both worlds")
        print("  4. Advanced Search      - Complex filters")
        print("  5. Faceted Navigation   - Exploration interface")
        print("  6. Similar Contracts    - Embedding similarity")
        print("  7. Index Management     - Create/update documents")
        print("  8. Analytics Tracking   - Performance metrics")
        print("\n✅ Your enterprise-grade search system is ready!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Error running examples: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()

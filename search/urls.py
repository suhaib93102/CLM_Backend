from django.urls import path
from .views import (
    SearchKeywordView,
    SearchSemanticView,
    SearchHybridView,
    SearchAdvancedView,
    SearchFacetsView,
    SearchFacetedView,
    SearchSuggestionsView,
    SearchIndexingView,
    SearchAnalyticsView
)

urlpatterns = [
    # Full-text keyword search: GET /api/search/?q=query
    path('', SearchKeywordView.as_view(), name='search-keyword'),
    
    # Semantic search: GET /api/search/semantic/?q=query
    path('semantic/', SearchSemanticView.as_view(), name='search-semantic'),
    
    # Hybrid search: POST /api/search/hybrid/
    path('hybrid/', SearchHybridView.as_view(), name='search-hybrid'),
    
    # Advanced filtered search: POST /api/search/advanced/
    path('advanced/', SearchAdvancedView.as_view(), name='search-advanced'),
    
    # Facets navigation: GET /api/search/facets/
    path('facets/', SearchFacetsView.as_view(), name='search-facets'),
    
    # Faceted search: POST /api/search/faceted/
    path('faceted/', SearchFacetedView.as_view(), name='search-faceted'),
    
    # Autocomplete suggestions: GET /api/search/suggestions/?q=query
    path('suggestions/', SearchSuggestionsView.as_view(), name='search-suggestions'),
    
    # Index management: POST /api/search/index/, DELETE /api/search/index/{id}/
    path('index/', SearchIndexingView.as_view(), name='search-indexing'),
    
    # Search analytics: GET /api/search/analytics/
    path('analytics/', SearchAnalyticsView.as_view(), name='search-analytics'),
]

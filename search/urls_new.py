"""
Search URL Routing - Corrected Architecture
Maps endpoints to views following the baseline assumption
No ML training required
"""
from django.urls import path
from .views_new import (
    DocumentUploadView,
    FullTextSearchView,
    SemanticSearchView,
    HybridSearchView,
    AdvancedSearchView,
    FacetsView,
    SimilarDocumentsView,
    SearchAnalyticsView,
)

urlpatterns = [
    # Document Ingestion
    path('upload/', DocumentUploadView.as_view(), name='search-upload'),
    
    # Search Endpoints
    path('fts/', FullTextSearchView.as_view(), name='search-fts'),  # Full-Text Search
    path('semantic/', SemanticSearchView.as_view(), name='search-semantic'),  # Semantic Search
    path('hybrid/', HybridSearchView.as_view(), name='search-hybrid'),  # Hybrid (best)
    path('advanced/', AdvancedSearchView.as_view(), name='search-advanced'),  # With filters
    
    # Navigation
    path('facets/', FacetsView.as_view(), name='search-facets'),  # Get facets
    path('similar/<uuid:document_id>/', SimilarDocumentsView.as_view(), name='search-similar'),
    
    # Analytics
    path('analytics/', SearchAnalyticsView.as_view(), name='search-analytics'),
]

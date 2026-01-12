from rest_framework import serializers
from .models import SearchIndexModel, SearchAnalyticsModel


class SearchIndexSerializer(serializers.ModelSerializer):
    """Serializer for search index results"""
    class Meta:
        model = SearchIndexModel
        fields = [
            'id',
            'entity_type',
            'entity_id',
            'title',
            'content',
            'keywords',
            'metadata',
            'created_at',
            'updated_at',
            'rank_score'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SearchResultSerializer(serializers.Serializer):
    """Serializer for formatted search results"""
    id = serializers.UUIDField()
    entity_type = serializers.CharField()
    entity_id = serializers.UUIDField()
    title = serializers.CharField()
    content = serializers.CharField()
    keywords = serializers.ListField(child=serializers.CharField())
    relevance_score = serializers.FloatField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()


class SearchAnalyticsSerializer(serializers.ModelSerializer):
    """Serializer for search analytics"""
    class Meta:
        model = SearchAnalyticsModel
        fields = [
            'id',
            'tenant_id',
            'user_id',
            'query',
            'query_type',
            'results_count',
            'response_time_ms',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class SearchFacetSerializer(serializers.Serializer):
    """Serializer for search facets"""
    name = serializers.CharField()
    count = serializers.IntegerField()
    value = serializers.CharField(required=False)


class SearchFacetResponseSerializer(serializers.Serializer):
    """Serializer for faceted search response"""
    entity_types = SearchFacetSerializer(many=True)
    keywords = SearchFacetSerializer(many=True)
    date_range = serializers.DictField()
    total_documents = serializers.IntegerField()


class AdvancedSearchFilterSerializer(serializers.Serializer):
    """Serializer for advanced search filters"""
    entity_type = serializers.CharField(required=False, allow_blank=True)
    date_from = serializers.DateTimeField(required=False, allow_null=True)
    date_to = serializers.DateTimeField(required=False, allow_null=True)
    keywords = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        default=[]
    )
    status = serializers.CharField(required=False, allow_blank=True)


class HybridSearchRequestSerializer(serializers.Serializer):
    """Serializer for hybrid search request"""
    query = serializers.CharField()
    limit = serializers.IntegerField(default=20, min_value=1, max_value=100)
    weights = serializers.DictField(required=False, default={
        'full_text': 0.6,
        'semantic': 0.4
    })

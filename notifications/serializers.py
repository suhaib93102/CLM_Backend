from rest_framework import serializers
from .models import NotificationModel

class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationModel
        fields = '__all__'
        read_only_fields = ['id', 'tenant_id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        if 'tenant_id' not in validated_data and self.context.get('request'):
            validated_data['tenant_id'] = self.context['request'].user.tenant_id
        return super().create(validated_data)

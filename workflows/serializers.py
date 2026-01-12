from rest_framework import serializers
from .models import Workflow, WorkflowInstance

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__'
        read_only_fields = ['id', 'tenant_id', 'created_by', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        if 'tenant_id' not in validated_data and self.context.get('request'):
            validated_data['tenant_id'] = self.context['request'].user.tenant_id
        if 'created_by' not in validated_data and self.context.get('request'):
            validated_data['created_by'] = self.context['request'].user.user_id
        return super().create(validated_data)

class WorkflowInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = WorkflowInstance
        fields = '__all__'

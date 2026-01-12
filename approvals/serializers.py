from rest_framework import serializers
from .models import ApprovalModel

class ApprovalSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApprovalModel
        fields = '__all__'
        read_only_fields = ['id', 'tenant_id', 'created_at']
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import ApprovalModel
from .serializers import ApprovalSerializer

class ApprovalViewSet(viewsets.ModelViewSet):
    queryset = ApprovalModel.objects.all()
    serializer_class = ApprovalSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)
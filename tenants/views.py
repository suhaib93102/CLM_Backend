from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import TenantModel
from .serializers import TenantSerializer

class TenantViewSet(viewsets.ModelViewSet):
    queryset = TenantModel.objects.all()
    serializer_class = TenantSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    @action(detail=True, methods=['get', 'post'])
    def users(self, request, id=None):
        if request.method == 'POST':
            return Response({'message': 'User added to tenant'}, status=status.HTTP_201_CREATED)
        return Response({'users': []})
    
    @action(detail=True, methods=['get'])
    def stats(self, request, id=None):
        tenant = self.get_object()
        return Response({'tenant_id': str(tenant.id), 'status': tenant.status})

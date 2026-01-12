from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import RepositoryModel, RepositoryFolderModel
from .serializers import RepositorySerializer, RepositoryFolderSerializer

class RepositoryViewSet(viewsets.ModelViewSet):
    queryset = RepositoryModel.objects.all()
    serializer_class = RepositorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id, created_by=self.request.user.user_id)
    
    @action(detail=True, methods=['get'])
    def versions(self, request, id=None):
        document = self.get_object()
        return Response({'versions': []})
    
    @action(detail=True, methods=['post'])
    def move(self, request, id=None):
        document = self.get_object()
        new_folder_id = request.data.get('folder_id')
        return Response({'message': 'Document moved', 'folder_id': new_folder_id})
    
    @action(detail=False, methods=['get', 'post'])
    def folders(self, request):
        if request.method == 'POST':
            return Response({'message': 'Folder created'}, status=status.HTTP_201_CREATED)
        folders = RepositoryFolderModel.objects.filter(tenant_id=request.user.tenant_id)
        return Response(RepositoryFolderSerializer(folders, many=True).data)

class RepositoryFolderViewSet(viewsets.ModelViewSet):
    queryset = RepositoryFolderModel.objects.all()
    serializer_class = RepositoryFolderSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id)

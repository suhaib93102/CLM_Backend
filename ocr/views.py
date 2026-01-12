from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import OCRJobModel
from .serializers import OCRJobSerializer

class OCRViewSet(viewsets.ModelViewSet):
    queryset = OCRJobModel.objects.all()
    serializer_class = OCRJobSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    @action(detail=False, methods=['post'])
    def process(self, request):
        try:
            document_id = request.data.get('document_id')
            if not document_id:
                return Response({'error': 'document_id required'}, status=status.HTTP_400_BAD_REQUEST)
            job = OCRJobModel.objects.create(
                tenant_id=request.user.tenant_id,
                document_id=document_id,
                status='processing'
            )
            return Response(OCRJobSerializer(job).data, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def status(self, request, id=None):
        job = self.get_object()
        return Response({'id': str(job.id), 'status': job.status})
    
    @action(detail=True, methods=['get'])
    def result(self, request, id=None):
        job = self.get_object()
        return Response({'text': job.extracted_text, 'confidence': job.confidence_score})

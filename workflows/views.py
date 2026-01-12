from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Workflow, WorkflowInstance
from .serializers import WorkflowSerializer, WorkflowInstanceSerializer

class WorkflowViewSet(viewsets.ModelViewSet):
    queryset = Workflow.objects.all()
    serializer_class = WorkflowSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'
    
    def perform_create(self, serializer):
        serializer.save(tenant_id=self.request.user.tenant_id, created_by=self.request.user.user_id)
    
    @action(detail=True, methods=['get'])
    def status(self, request, id=None):
        workflow = self.get_object()
        instances = WorkflowInstance.objects.filter(workflow=workflow).order_by('-created_at')[:5]
        return Response({
            'workflow_id': str(workflow.id),
            'status': workflow.status,
            'recent_instances': WorkflowInstanceSerializer(instances, many=True).data
        })
    
    @action(detail=True, methods=['get'])
    def instances(self, request, id=None):
        """GET /workflows/{id}/instances/
        
        Get all instances of this workflow
        """
        workflow = self.get_object()
        instances = WorkflowInstance.objects.filter(
            workflow=workflow
        ).order_by('-created_at')
        
        return Response({
            'workflow_id': str(workflow.id),
            'workflow_name': workflow.name,
            'total_instances': instances.count(),
            'instances': WorkflowInstanceSerializer(instances, many=True).data
        })
    
    @action(detail=False, methods=['get'])
    def config(self, request):
        return Response({
            'available_steps': ['initiate', 'approve', 'execute', 'complete'],
            'available_transitions': {
                'draft': ['active'],
                'active': ['archived'],
                'archived': []
            }
        })

class WorkflowInstanceViewSet(viewsets.ModelViewSet):
    queryset = WorkflowInstance.objects.all()
    serializer_class = WorkflowInstanceSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

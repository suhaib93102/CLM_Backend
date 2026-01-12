from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from authentication.models import User
from contracts.models import Contract
from tenants.models import TenantModel

class AdminViewSet(viewsets.ViewSet):
    """Admin panel endpoints"""
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'], url_path='sla-rules')
    def sla_rules(self, request):
        """
        GET /api/admin/sla-rules/
        Get all SLA rules for the tenant
        """
        tenant_id = request.user.tenant_id
        
        sla_rules = [
            {
                "id": "sla-1",
                "name": "Standard SLA",
                "description": "Standard service level agreement",
                "tenant_id": str(tenant_id),
                "response_time": 24,  # hours
                "resolution_time": 72,
                "priority_levels": ["Low", "Medium", "High", "Critical"],
                "created_at": timezone.now().isoformat(),
                "updated_at": timezone.now().isoformat()
            },
            {
                "id": "sla-2",
                "name": "Premium SLA",
                "description": "Premium service level agreement",
                "tenant_id": str(tenant_id),
                "response_time": 4,
                "resolution_time": 24,
                "priority_levels": ["Low", "Medium", "High", "Critical"],
                "created_at": timezone.now().isoformat(),
                "updated_at": timezone.now().isoformat()
            }
        ]
        
        return Response({"sla_rules": sla_rules})
    
    @action(detail=False, methods=['get'], url_path='sla-breaches')
    def sla_breaches(self, request):
        """
        GET /api/admin/sla-breaches/
        Get SLA breaches for the tenant
        """
        tenant_id = request.user.tenant_id
        
        breaches = []
        
        return Response({"sla_breaches": breaches, "total": 0})
    
    @action(detail=False, methods=['get'], url_path='users/roles')
    def user_roles(self, request):
        """
        GET /api/admin/users/roles/
        Get user roles and assignments
        """
        tenant_id = request.user.tenant_id
        
        users = User.objects.filter(tenant_id=tenant_id)
        user_roles = [
            {
                "user_id": str(u.user_id),
                "email": u.email,
                "name": f"{u.first_name} {u.last_name}".strip() or u.email,
                "roles": ["admin" if u.is_staff else "user"],
                "is_active": u.is_active,
                "last_login": u.last_login.isoformat() if u.last_login else None,
                "date_joined": u.date_joined.isoformat()
            }
            for u in users
        ]
        
        return Response({"user_roles": user_roles})
    
    @action(detail=False, methods=['get'], url_path='tenants')
    def list_tenants(self, request):
        """
        GET /api/admin/tenants/
        List tenants (current user's tenant if not admin)
        """
        if request.user.is_staff:
            tenants = TenantModel.objects.all()
        else:
            # Non-admin users see only their tenant
            tenants = TenantModel.objects.filter(id=request.user.tenant_id)
        
        tenant_data = [
            {
                "id": str(t.id),
                "name": t.name,
                "created_at": t.created_at.isoformat()
            }
            for t in tenants
        ]
        
        return Response({"tenants": tenant_data})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_roles(request):
    """
    GET /api/roles/
    List all available roles
    """
    roles = [
        {"id": "admin", "name": "Administrator", "description": "Full system access"},
        {"id": "user", "name": "User", "description": "Standard user access"},
        {"id": "viewer", "name": "Viewer", "description": "Read-only access"},
        {"id": "manager", "name": "Manager", "description": "Team management access"},
    ]
    
    return Response({"roles": roles})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_permissions(request):
    """
    GET /api/permissions/
    List all available permissions
    """
    permissions = [
        {"id": "view_contracts", "name": "View Contracts", "category": "Contracts"},
        {"id": "create_contracts", "name": "Create Contracts", "category": "Contracts"},
        {"id": "edit_contracts", "name": "Edit Contracts", "category": "Contracts"},
        {"id": "delete_contracts", "name": "Delete Contracts", "category": "Contracts"},
        {"id": "view_templates", "name": "View Templates", "category": "Templates"},
        {"id": "create_templates", "name": "Create Templates", "category": "Templates"},
        {"id": "view_users", "name": "View Users", "category": "Administration"},
        {"id": "manage_users", "name": "Manage Users", "category": "Administration"},
        {"id": "view_audit_logs", "name": "View Audit Logs", "category": "Administration"},
    ]
    
    return Response({"permissions": permissions})


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def list_users(request):
    """
    GET /api/users/
    List all users in the tenant
    """
    tenant_id = request.user.tenant_id
    
    users = User.objects.filter(tenant_id=tenant_id)
    user_data = [
        {
            "id": str(u.user_id),
            "email": u.email,
            "first_name": u.first_name,
            "last_name": u.last_name,
            "is_active": u.is_active,
            "is_staff": u.is_staff,
            "date_joined": u.date_joined.isoformat(),
            "last_login": u.last_login.isoformat() if u.last_login else None,
        }
        for u in users
    ]
    
    return Response({"users": user_data, "total": len(user_data)})

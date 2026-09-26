from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from functools import wraps
from branding.models import BrandProject
from .models import TeamMember, Role

def get_user_project_role(user, project):
    """
    Returns the user's role on the project.
    If the user is the owner, returns Role.OWNER.
    Otherwise, looks up TeamMember.
    Returns None if no access.
    """
    if project.user == user:
        return Role.OWNER
        
    team_member = TeamMember.objects.filter(project=project, user=user).first()
    if team_member:
        return team_member.role
    return None

def has_project_access(user, project):
    return get_user_project_role(user, project) is not None

def require_project_access(view_func):
    """
    Decorator for functional views that take 'pk' as the project ID.
    Ensures the user has at least Viewer access to the project.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        pk = kwargs.get('pk')
        project = get_object_or_404(BrandProject, pk=pk)
        
        if not has_project_access(request.user, project):
            raise PermissionDenied("You do not have access to this workspace.")
            
        return view_func(request, *args, **kwargs)
    return _wrapped_view

class ProjectAccessMixin:
    """
    Mixin for class-based views. Assumes self.kwargs['pk'] is the project ID.
    """
    def dispatch(self, request, *args, **kwargs):
        pk = self.kwargs.get('pk')
        project = get_object_or_404(BrandProject, pk=pk)
        
        if not has_project_access(request.user, project):
            raise PermissionDenied("You do not have access to this workspace.")
            
        return super().dispatch(request, *args, **kwargs)

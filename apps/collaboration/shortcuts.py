from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from branding.models import BrandProject
from collaboration.permissions import has_project_access

def get_project_for_user(pk, user):
    project = get_object_or_404(BrandProject, pk=pk)
    if not has_project_access(user, project):
        raise PermissionDenied("You do not have access to this workspace.")
    return project

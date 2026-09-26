from django.db import models
from django.conf import settings
from branding.models import BrandProject

class TemplateCategory(models.TextChoices):
    BRAND = 'BRAND', 'Brand Template'
    CAMPAIGN = 'CAMPAIGN', 'Campaign Template'
    MARKETING = 'MARKETING', 'Marketing Template'
    SOCIAL = 'SOCIAL', 'Social Template'
    EMAIL = 'EMAIL', 'Email Template'
    POSTER = 'POSTER', 'Poster Template'

class BrandTemplate(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=20, choices=TemplateCategory.choices)
    
    # Store the actual template structure as JSON
    content_payload = models.JSONField()
    
    # Optional image preview
    preview_image = models.ImageField(upload_to='templates/previews/', null=True, blank=True)
    
    # Link to a project if it's a custom template saved from an existing project
    source_project = models.ForeignKey(BrandProject, on_delete=models.SET_NULL, null=True, blank=True, related_name='created_templates')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_templates')
    created_at = models.DateTimeField(auto_now_add=True)
    
    # If is_global is True, it's a system template available to all workspaces
    is_global = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} ({self.category})"

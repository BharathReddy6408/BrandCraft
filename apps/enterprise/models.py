from django.db import models
from django.conf import settings
from branding.models import BrandProject
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
import uuid
from django.utils import timezone
from datetime import timedelta

class AssetCollection(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='collections')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_collections')
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.name} ({self.project.business_name})"

class CollectionItem(models.Model):
    collection = models.ForeignKey(AssetCollection, on_delete=models.CASCADE, related_name='items')
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    added_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('collection', 'content_type', 'object_id')

class WorkspaceItemMeta(models.Model):
    """
    Stores user-specific metadata about any item in the workspace (Favorites, Pins, Recently Used).
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='workspace_meta')
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='workspace_meta')
    
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    item = GenericForeignKey('content_type', 'object_id')
    
    is_favorite = models.BooleanField(default=False)
    is_pinned = models.BooleanField(default=False)
    last_accessed = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ('user', 'content_type', 'object_id')

def default_expiration():
    return timezone.now() + timedelta(days=7)

class SharedLink(models.Model):
    """
    Secure sharing for Client Presentation or specific assets.
    """
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='shared_links')
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    
    # Optional specific item to share. If null, it shares the Brand Presentation Mode.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    shared_item = GenericForeignKey('content_type', 'object_id')
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=default_expiration)
    
    # Optional password protection (store hashed)
    password_hash = models.CharField(max_length=128, blank=True, null=True)
    is_revoked = models.BooleanField(default=False)

    def is_valid(self):
        return not self.is_revoked and timezone.now() < self.expires_at

class ChangeHistory(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='history_logs')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    action = models.CharField(max_length=255) # e.g., "Updated Logo", "Approved Campaign"
    
    content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    target_item = GenericForeignKey('content_type', 'object_id')
    
    previous_value = models.JSONField(null=True, blank=True)
    current_value = models.JSONField(null=True, blank=True)
    
    timestamp = models.DateTimeField(auto_now_add=True)

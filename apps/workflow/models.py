from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from branding.models import BrandProject
import uuid

class WorkflowState(models.Model):
    STAGES = (
        ('SETUP', 'Brand Setup'),
        ('DNA', 'Brand DNA'),
        ('LOGO', 'Logo'),
        ('IDENTITY', 'Identity'),
        ('CREATIVE', 'Creative Assets'),
        ('MARKETING', 'Marketing'),
        ('SOCIAL', 'Social'),
        ('CAMPAIGN', 'Campaign'),
        ('INTELLIGENCE', 'Brand Intelligence'),
        ('KIT', 'Brand Kit'),
        ('REPORTS', 'Executive Reports'),
        ('LAUNCH', 'Launch')
    )

    project = models.OneToOneField(BrandProject, on_delete=models.CASCADE, related_name='workflow_state')
    current_stage = models.CharField(max_length=20, choices=STAGES, default='SETUP')
    completed_stages = models.JSONField(default=list, blank=True)
    blocked_stages = models.JSONField(default=list, blank=True)
    completion_percentage = models.IntegerField(default=0)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.project.business_name} - {self.current_stage}"

class ApprovalItem(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('PENDING', 'Pending Approval'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
        ('ARCHIVED', 'Archived')
    )

    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='approval_items')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Generic relation to tie to MarketingContent, SocialPost, Campaign, etc.
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')
    
    item_type = models.CharField(max_length=50, help_text="e.g., Logo, Social Post, Campaign")
    title = models.CharField(max_length=255)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    feedback = models.TextField(blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"[{self.status}] {self.item_type}: {self.title}"

class ContentVersion(models.Model):
    approval_item = models.ForeignKey(ApprovalItem, on_delete=models.CASCADE, related_name='versions')
    version_number = models.PositiveIntegerField(default=1)
    payload = models.JSONField(help_text="Snapshot of the content data")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-version_number']
        unique_together = ('approval_item', 'version_number')

class PlannerRecommendation(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='planner_recommendations')
    action_type = models.CharField(max_length=50) # e.g., 'GENERATE_LOGO', 'APPROVE_CONTENT'
    title = models.CharField(max_length=255)
    description = models.TextField()
    reason = models.TextField(help_text="AI explanation for why this is recommended")
    estimated_minutes = models.IntegerField(default=2)
    priority = models.IntegerField(default=1) # Lower is higher priority
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['priority', '-created_at']

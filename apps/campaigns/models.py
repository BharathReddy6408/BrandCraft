from django.db import models
from django.conf import settings
from branding.models import BrandProject
from brand_assets.models import BrandAsset
from socialmedia.models import SocialPost
from marketing.models import MarketingContent

class Campaign(models.Model):
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('GENERATED', 'Generated'),
        ('ACTIVE', 'Active'),
        ('COMPLETED', 'Completed'),
        ('ARCHIVED', 'Archived'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='campaigns', null=True, blank=True)
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='campaigns')
    
    name = models.CharField(max_length=255)
    goal = models.CharField(max_length=255, blank=True, null=True)
    duration = models.CharField(max_length=100, blank=True, null=True)
    platforms = models.JSONField(blank=True, null=True, help_text="List of target platforms")
    
    strategy = models.TextField(blank=True, null=True)
    audience_focus = models.TextField(blank=True, null=True)
    content_pillars = models.JSONField(blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Campaign: {self.name} for {self.project.business_name}"

class CampaignItem(models.Model):
    STATUS_CHOICES = (
        ('PLANNED', 'Planned'),
        ('GENERATED', 'Generated'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
    )
    
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='items')
    
    scheduled_day = models.IntegerField(help_text="Day of the campaign (e.g., 1, 3, 5)")
    scheduled_date = models.DateField(blank=True, null=True)
    
    platform = models.CharField(max_length=50, blank=True, null=True)
    content_type = models.CharField(max_length=100, blank=True, null=True)
    topic = models.CharField(max_length=255, blank=True, null=True)
    objective = models.CharField(max_length=255, blank=True, null=True)
    
    # Links to generated content
    social_post = models.ForeignKey(SocialPost, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaign_items')
    marketing_content = models.ForeignKey(MarketingContent, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaign_items')
    creative_asset = models.ForeignKey(BrandAsset, on_delete=models.SET_NULL, null=True, blank=True, related_name='campaign_items')
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PLANNED')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['scheduled_day']
        
    def __str__(self):
        return f"{self.campaign.name} - Day {self.scheduled_day} - {self.platform}"

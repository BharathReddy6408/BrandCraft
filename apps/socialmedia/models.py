from django.db import models
from django.conf import settings
from branding.models import BrandProject
from brand_assets.models import BrandAsset

class SocialPost(models.Model):
    PLATFORMS = (
        ('INSTAGRAM', 'Instagram'),
        ('TWITTER', 'Twitter'),
        ('LINKEDIN', 'LinkedIn'),
        ('FACEBOOK', 'Facebook'),
    )
    
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('GENERATED', 'Generated'),
        ('APPROVED', 'Approved'),
        ('PUBLISHED', 'Published'),
        ('ARCHIVED', 'Archived'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='social_posts', null=True, blank=True)
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='social_posts')
    asset_link = models.OneToOneField(BrandAsset, on_delete=models.SET_NULL, null=True, blank=True)
    
    platform = models.CharField(max_length=20, choices=PLATFORMS)
    title = models.CharField(max_length=255, blank=True, null=True, help_text="Topic or Title")
    caption = models.TextField(blank=True, null=True)
    hashtags = models.TextField(blank=True, null=True)
    content_json = models.JSONField(blank=True, null=True, help_text="Structured content (headline, cta, image_prompt)")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATED')
    prompt_metadata = models.JSONField(blank=True, null=True, help_text="Data used to generate this post")
    provider = models.CharField(max_length=100, blank=True, null=True, default='Groq')
    model_name = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_platform_display()} Post - {self.project.business_name}"

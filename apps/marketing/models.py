from django.db import models
from django.conf import settings
from branding.models import BrandProject
from brand_assets.models import BrandAsset, AssetCategory

class MarketingContent(models.Model):
    CONTENT_TYPES = (
        ('BLOG', 'Blog Post'),
        ('LANDING_PAGE', 'Landing Page Copy'),
        ('EMAIL', 'Email Campaign'),
        ('AD', 'Advertisement Copy'),
        ('SEO', 'SEO Metadata'),
    )
    
    STATUS_CHOICES = (
        ('DRAFT', 'Draft'),
        ('GENERATED', 'Generated'),
        ('APPROVED', 'Approved'),
        ('ARCHIVED', 'Archived'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='marketing_contents', null=True, blank=True)
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='marketing_contents')
    asset_link = models.OneToOneField(BrandAsset, on_delete=models.SET_NULL, null=True, blank=True)
    
    content_type = models.CharField(max_length=20, choices=CONTENT_TYPES)
    title = models.CharField(max_length=255)
    
    # Store plain text body (if needed) or structured json
    body = models.TextField(blank=True, null=True)
    content_json = models.JSONField(blank=True, null=True, help_text="Structured content data")
    
    tone = models.CharField(max_length=100, blank=True, null=True)
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATED')
    prompt_metadata = models.JSONField(blank=True, null=True, help_text="Data used to generate this content")
    provider = models.CharField(max_length=100, blank=True, null=True, default='Groq')
    model_name = models.CharField(max_length=100, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.get_content_type_display()} - {self.title}"

    @property
    def safe_json_string(self):
        import json
        if not self.content_json:
            return "{}"
        return json.dumps(self.content_json)

    @property
    def snippet(self):
        import re
        if not self.content_json:
            return "No preview available."
        
        values = list(self.content_json.values())
        text = " ".join([str(v) for v in values if isinstance(v, str)])
        # Strip HTML tags like <br/> and replace them with spaces
        text = re.sub(r'<[^>]+>', ' ', text)
        # Collapse multiple spaces
        text = re.sub(r'\s+', ' ', text).strip()
        return (text[:77] + '...') if len(text) > 80 else text

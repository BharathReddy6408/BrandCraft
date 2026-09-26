from django.db import models
from branding.models import BrandProject
from django.conf import settings

class AssetCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name

class BrandAsset(models.Model):
    ASSET_TYPES = (
        ('BUSINESS_NAME', 'Business Name'),
        ('SLOGAN', 'Slogan'),
        ('LOGO', 'Logo'),
        ('LOGO_PROMPT', 'Logo Prompt'),
        ('BRAND_GUIDELINE', 'Brand Guideline'),
        ('SOCIAL_POST', 'Social Post'),
        ('SOCIAL_GRAPHIC', 'Social Graphic'),
        ('AD_CREATIVE', 'Ad Creative'),
        ('POSTER', 'Poster'),
        ('BANNER', 'Banner'),
        ('BUSINESS_CARD', 'Business Card'),
        ('LETTERHEAD', 'Letterhead'),
        ('EMAIL_HEADER', 'Email Header'),
        ('CAMPAIGN', 'Campaign'),
        ('MARKETING_COPY', 'Marketing Copy'),
        # Keep legacy mapping for backwards compat
        ('NAME', 'Business Name (Legacy)'),
        ('TAGLINE', 'Tagline (Legacy)'),
        ('STORY', 'Brand Story (Legacy)'),
        ('PERSONALITY', 'Personality (Legacy)'),
        ('VOICE', 'Brand Voice (Legacy)'),
        ('COLOR', 'Color Palette (Legacy)'),
        ('TYPOGRAPHY', 'Typography Set (Legacy)'),
    )
    STATUS_CHOICES = [
        ('GENERATING', 'Generating'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
        ('ARCHIVED', 'Archived'),
        # Legacy
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('FLAGGED', 'Flagged'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='brand_assets', null=True, blank=True)
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='assets')
    asset_type = models.CharField(max_length=50, choices=ASSET_TYPES, default='SOCIAL_POST', db_index=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, blank=True) # Kept for backward compatibility
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='READY')
    
    title = models.CharField(max_length=255, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    
    content_json = models.JSONField(blank=True, null=True)
    file_upload = models.FileField(upload_to='brand_assets/', blank=True, null=True)
    
    thumbnail = models.ImageField(upload_to='brand_assets/thumbnails/', blank=True, null=True)
    prompt = models.TextField(blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True)
    
    provider = models.CharField(max_length=50, blank=True, null=True)
    model_name = models.CharField(max_length=100, blank=True, null=True)
    
    tags = models.JSONField(default=list, blank=True)
    
    is_favorite = models.BooleanField(default=False)
    is_selected = models.BooleanField(default=False)
    version = models.IntegerField(default=1)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title or self.get_asset_type_display()} - {self.project.business_name}"

class AssetVersion(models.Model):
    asset = models.ForeignKey(BrandAsset, on_delete=models.CASCADE, related_name='versions')
    version_number = models.IntegerField(default=1)
    content_json = models.JSONField(blank=True, null=True)
    file_upload = models.FileField(upload_to='brand_assets/versions/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.asset.title} v{self.version_number}"

class BrandTemplate(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(AssetCategory, on_delete=models.SET_NULL, null=True, related_name='templates')
    thumbnail = models.ImageField(upload_to='brand_templates/thumbnails/', blank=True, null=True)
    file = models.FileField(upload_to='brand_templates/files/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

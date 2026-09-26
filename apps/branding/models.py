from django.db import models
from django.conf import settings

class BrandProject(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='brand_projects')
    business_name = models.CharField(max_length=255, blank=True, null=True)
    business_idea = models.TextField(blank=True, null=True)
    industry = models.CharField(max_length=150, blank=True, null=True)
    target_audience = models.TextField(blank=True, null=True)
    
    # STRATEGY
    business_goal = models.TextField(blank=True, null=True)
    brand_mission = models.TextField(blank=True, null=True)
    brand_vision = models.TextField(blank=True, null=True)
    brand_values = models.JSONField(blank=True, null=True)
    usp = models.TextField(blank=True, null=True)
    keywords = models.JSONField(blank=True, null=True)
    
    # PERSONALITY
    brand_personality = models.CharField(max_length=255, blank=True, null=True)
    brand_voice = models.TextField(blank=True, null=True)
    
    # VISUAL IDENTITY
    preferred_style = models.CharField(max_length=255, blank=True, null=True)
    visual_style = models.CharField(max_length=255, blank=True, null=True)
    preferred_colors = models.JSONField(blank=True, null=True)
    primary_color = models.CharField(max_length=50, blank=True, null=True)
    secondary_color = models.CharField(max_length=50, blank=True, null=True)
    accent_color = models.CharField(max_length=50, blank=True, null=True)
    background_color = models.CharField(max_length=50, blank=True, null=True)
    heading_font = models.CharField(max_length=100, blank=True, null=True)
    body_font = models.CharField(max_length=100, blank=True, null=True)
    logo_direction = models.TextField(blank=True, null=True)
    
    # SYSTEM
    completion_score = models.PositiveSmallIntegerField(default=0)
    generation_status = models.CharField(max_length=50, default='DRAFT')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.business_name or 'Untitled Project'} - {self.user.email}"

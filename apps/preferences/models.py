from django.db import models
from django.conf import settings
from branding.models import BrandProject

class AutomationRule(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='automation_rules')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    rule_type = models.CharField(max_length=50) # e.g., 'SEASONAL_CAMPAIGN', 'WEEKLY_SOCIAL'
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    is_enabled = models.BooleanField(default=False)
    
    # Store settings or criteria (e.g. which platforms to auto-draft for)
    config = models.JSONField(default=dict, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('project', 'rule_type')

    def __str__(self):
        return f"{self.project.business_name} - {self.name} ({'Enabled' if self.is_enabled else 'Disabled'})"

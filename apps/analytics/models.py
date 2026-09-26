from django.db import models
from django.conf import settings
from branding.models import BrandProject

class BrandAudit(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='audits')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    # Deterministic Scores
    foundation_score = models.IntegerField(default=0)
    activation_score = models.IntegerField(default=0)
    content_coverage_score = models.IntegerField(default=0)
    campaign_readiness_score = models.IntegerField(default=0)
    
    # AI Evaluated Scores
    consistency_score = models.IntegerField(default=0, help_text="AI evaluated consistency 0-100")
    
    # Overall (Derived)
    overall_score = models.IntegerField(default=0)
    
    # Structured AI Feedback
    summary = models.TextField(blank=True)
    strengths = models.JSONField(default=list, blank=True)
    weaknesses = models.JSONField(default=list, blank=True)
    opportunities = models.JSONField(default=list, blank=True)
    
    # Priority Actions (Structured JSON for Recommendations Engine)
    priority_actions = models.JSONField(default=list, blank=True)
    
    status = models.CharField(max_length=20, choices=[
        ('NOT_RUN', 'Not Run'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('STALE', 'Stale')
    ], default='NOT_RUN')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Audit for {self.project.business_name} - {self.created_at.strftime('%Y-%m-%d')}"

class BrandRecommendation(models.Model):
    PRIORITY_CHOICES = [
        ('HIGH', 'High Priority'),
        ('MEDIUM', 'Medium Priority'),
        ('LOW', 'Low Priority')
    ]
    
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='recommendations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='MEDIUM')
    title = models.CharField(max_length=255)
    reason = models.TextField()
    module_destination = models.CharField(max_length=50, blank=True, help_text="URL name or module constant")
    
    is_dismissed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.get_priority_display()}: {self.title}"

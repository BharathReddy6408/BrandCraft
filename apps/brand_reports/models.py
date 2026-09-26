from django.db import models
from django.conf import settings
from branding.models import BrandProject
import uuid
import os

def report_file_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.report_type.lower()}_{instance.version}_{uuid.uuid4().hex[:8]}.{ext}"
    return os.path.join('brandcraft', 'users', str(instance.user.id), 'projects', str(instance.project.id), 'reports', filename)

class BrandReport(models.Model):
    REPORT_TYPES = (
        ('STRATEGY', 'Brand Strategy'),
        ('IDENTITY', 'Brand Identity'),
        ('AUDIT', 'Brand Audit'),
        ('CAMPAIGN', 'Campaign Report'),
        ('EXECUTIVE', 'Executive Brand Report'),
        ('GUIDELINES', 'Brand Guidelines'),
    )
    
    STATUS_CHOICES = (
        ('GENERATING', 'Generating'),
        ('READY', 'Ready'),
        ('FAILED', 'Failed'),
        ('ARCHIVED', 'Archived'),
    )

    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='reports')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='brand_reports')
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES)
    title = models.CharField(max_length=255)
    version = models.IntegerField(default=1)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='GENERATING')
    
    data_snapshot = models.JSONField(default=dict, blank=True, help_text="Snapshot of the data used to generate this report.")
    file = models.FileField(upload_to=report_file_path, null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ('project', 'report_type', 'version')

    def __str__(self):
        return f"{self.project.business_name} - {self.get_report_type_display()} v{self.version}"

    @property
    def is_stale(self):
        # Could implement logic here to check if project.updated_at > self.created_at
        return self.project.updated_at > self.created_at

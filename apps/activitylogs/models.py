from django.db import models
from django.conf import settings
from branding.models import BrandProject

class ActivityLog(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='activity_logs', null=True, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    action = models.CharField(max_length=255, default='Unknown Action')
    description = models.TextField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.action} - {self.timestamp}'

from django.db import models

class SystemSettings(models.Model):
    key = models.CharField(max_length=100, unique=True)
    value = models.TextField()
    description = models.TextField(blank=True, null=True)
    
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.key}: {self.value}"

class MaintenanceWindow(models.Model):
    title = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    
    is_active = models.BooleanField(default=False)
    message = models.TextField(default="BrandCraft is undergoing scheduled maintenance. We'll be back online shortly.")
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Maintenance: {self.title} ({self.start_time} to {self.end_time})"

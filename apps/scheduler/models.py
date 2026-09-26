from django.db import models
from django.conf import settings

class TaskSchedule(models.Model):
    TASK_TYPES = (
        ('GENERATE_REPORT', 'Generate Brand Report'),
        ('SOCIAL_POST', 'Publish Social Media Post'),
        ('CLEAR_CACHE', 'Clear System Cache'),
    )
    
    STATUS_CHOICES = (
        ('PENDING', 'Pending'),
        ('RUNNING', 'Running'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='scheduled_tasks')
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    scheduled_time = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    
    payload = models.JSONField(blank=True, null=True, help_text="Parameters for the task execution")
    result = models.TextField(blank=True, null=True, help_text="Execution outputs or errors")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_task_type_display()} - {self.status} (Scheduled for {self.scheduled_time})"

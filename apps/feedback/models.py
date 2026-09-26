from django.db import models
from django.conf import settings

class UserFeedback(models.Model):
    RATING_CHOICES = (
        (1, '1 Star'),
        (2, '2 Stars'),
        (3, '3 Stars'),
        (4, '4 Stars'),
        (5, '5 Stars'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feedbacks')
    rating = models.IntegerField(choices=RATING_CHOICES)
    comments = models.TextField()
    
    source_page = models.CharField(max_length=255, blank=True, null=True, help_text="Page the user was on when submitting")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.email} - {self.rating} Stars at {self.created_at}"

class FeatureRequest(models.Model):
    STATUS_CHOICES = (
        ('PENDING', 'Pending Review'),
        ('PLANNED', 'Planned'),
        ('IN_DEVELOPMENT', 'In Development'),
        ('COMPLETED', 'Completed'),
        ('DECLINED', 'Declined'),
    )
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feature_requests')
    title = models.CharField(max_length=255)
    description = models.TextField()
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    upvotes = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} ({self.status}) by {self.user.email}"

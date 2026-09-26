from django.db import models

class SystemPerformance(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    metric = models.CharField(max_length=255, default='cpu')
    value = models.FloatField(default=0.0)

class SystemError(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    error_message = models.TextField(default='')
class APIMetric(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)
    endpoint = models.CharField(max_length=255)
    response_time = models.FloatField(default=0.0)
    status_code = models.IntegerField(default=200)

from django.db import models

class PromptTemplate(models.Model):
    name = models.CharField(max_length=100, unique=True)
    template_content = models.TextField(help_text="Use {{ variable }} for injection")
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name

class ModelConfiguration(models.Model):
    name = models.CharField(max_length=100)
    api_key_env_var = models.CharField(max_length=100, default='GET_API_KEY')
    model_name = models.CharField(max_length=100, default='llama-3.1-70b-versatile')
    temperature = models.FloatField(default=0.7)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name

from django.conf import settings

class ChatConversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='chat_conversations')
    brand_project = models.ForeignKey('branding.BrandProject', on_delete=models.CASCADE, related_name='chat_conversations')
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.brand_project.business_name})"

class ChatMessage(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20, choices=[('user', 'User'), ('ai', 'AI')])
    content = models.TextField()
    message_type = models.CharField(max_length=50, default='text')
    tool_name = models.CharField(max_length=100, blank=True, null=True)
    metadata = models.JSONField(blank=True, null=True, default=dict)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']

class ChatArtifact(models.Model):
    conversation = models.ForeignKey(ChatConversation, on_delete=models.CASCADE, related_name='artifacts')
    brand_project = models.ForeignKey('branding.BrandProject', on_delete=models.CASCADE)
    artifact_type = models.CharField(max_length=50) # e.g., 'logo_prompt', 'slogan_list'
    object_id = models.IntegerField(blank=True, null=True) # ID of an associated real model if saved
    title = models.CharField(max_length=255)
    content_json = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

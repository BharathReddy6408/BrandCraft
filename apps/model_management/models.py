from django.db import models

class AIModel(models.Model):
    MODEL_TYPES = (
        ('TEXT', 'Text Generation (LLM)'),
        ('IMAGE', 'Image Generation (Diffusion)'),
        ('EMBEDDING', 'Embedding Model (RAG)'),
    )
    
    STATUS_CHOICES = (
        ('ACTIVE', 'Active (In Production)'),
        ('INACTIVE', 'Inactive'),
        ('TESTING', 'Testing (A/B)'),
        ('DEPRECATED', 'Deprecated'),
    )
    
    name = models.CharField(max_length=255)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    version = models.CharField(max_length=50)
    
    provider_name = models.CharField(max_length=100, default='HuggingFace', help_text="e.g., OpenAI, Anthropic, Custom")
    api_identifier = models.CharField(max_length=255, help_text="Model path or key name used to call the API")
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='INACTIVE')
    api_key = models.CharField(max_length=255, blank=True, null=True, help_text="API Key for the model")
    is_fine_tuned = models.BooleanField(default=False)
    
    performance_score = models.FloatField(blank=True, null=True, help_text="Average accuracy or preference rating")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} v{self.version} ({self.get_model_type_display()}) - {self.status}"

class Dataset(models.Model):
    DATASET_TYPES = (
        ('TEXT', 'Text (CSV/JSONL)'),
        ('IMAGE', 'Images (ZIP)'),
    )
    STATUS_CHOICES = (
        ('RAW', 'Raw Uploaded'),
        ('PREPROCESSING', 'Preprocessing...'),
        ('READY', 'Ready for Training'),
        ('ERROR', 'Error'),
    )
    
    name = models.CharField(max_length=255)
    dataset_type = models.CharField(max_length=20, choices=DATASET_TYPES)
    file = models.FileField(upload_to='datasets/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RAW')
    record_count = models.IntegerField(default=0, help_text="Number of text rows or images")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.name} ({self.get_dataset_type_display()})"

class ModelTrainingJob(models.Model):
    STATUS_CHOICES = (
        ('QUEUED', 'Queued'),
        ('TRAINING', 'Training'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
    )
    
    base_model = models.ForeignKey(AIModel, on_delete=models.CASCADE, related_name='training_jobs')
    dataset = models.ForeignKey(Dataset, on_delete=models.CASCADE, related_name='training_jobs')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='QUEUED')
    
    epochs = models.IntegerField(default=3)
    batch_size = models.IntegerField(default=8)
    learning_rate = models.FloatField(default=0.0001)
    
    current_epoch = models.IntegerField(default=0)
    final_accuracy = models.FloatField(null=True, blank=True)
    final_loss = models.FloatField(null=True, blank=True)
    
    training_logs = models.TextField(blank=True, null=True, help_text="JSON serialized list of epoch metrics")
    
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"Training {self.base_model.name} on {self.dataset.name}"

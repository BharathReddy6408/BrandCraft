from django.db import models
from branding.models import BrandProject

class Document(models.Model):
    project = models.ForeignKey(BrandProject, on_delete=models.CASCADE, related_name='documents', null=True, blank=True)
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='knowledge_base/documents/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    is_processed = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.title} ({self.project.business_name})"

class DocumentChunk(models.Model):
    document = models.ForeignKey(Document, on_delete=models.CASCADE, related_name='chunks')
    content = models.TextField()
    chunk_index = models.IntegerField()
    embedding_id = models.CharField(max_length=255, blank=True, null=True) # ID mapping to FAISS index

    def __str__(self):
        return f"Chunk {self.chunk_index} of {self.document.title}"

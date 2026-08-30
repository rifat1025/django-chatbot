from django.db import models
from django.conf import settings


class KnowledgeDocument(models.Model):
    """A source document ingested into the vector store."""
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='documents')
    title = models.CharField(max_length=255)
    file = models.FileField(upload_to='knowledge_docs/', blank=True, null=True)
    raw_text = models.TextField(blank=True)  # for text pasted directly instead of a file
    chunk_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Conversation(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='conversations')
    title = models.CharField(max_length=255, default='New Conversation')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} — {self.title}"


class Message(models.Model):
    ROLE_CHOICES = (('user', 'User'), ('assistant', 'Assistant'))

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content = models.TextField()
    sources = models.JSONField(default=list, blank=True)  # retrieved chunks used for this answer
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']
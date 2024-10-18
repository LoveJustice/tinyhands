from django.db import models
from django.db.models import JSONField


class ChatbotHistoricalQuestion(models.Model):
    question = models.TextField(null=False)
    query = models.TextField(null=True)
    tags = JSONField(null=True)
    topic = models.CharField(null=True, max_length=200)
    date_time_entered = models.DateTimeField(auto_now_add=True)
    date_time_last_updated = models.DateTimeField(auto_now=True)
    date_time_added_to_vector_store = models.DateTimeField(null=True)

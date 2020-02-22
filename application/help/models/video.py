from django.db import models

class Video(models.Model):
    title = models.CharField('Title', max_length=255)
    description = models.TextField('Description', blank=True)
    url = models.CharField('Url', max_length=255)
    tags = models.TextField('Tags', blank=True)
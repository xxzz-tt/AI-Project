from django.db import models

# Create your models here.

class Video(models.Model):
    name = models.CharField(max_length=150)
    video_link = models.CharField(max_length=150)
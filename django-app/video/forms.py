from django import forms
from django.forms import ModelForm
from .models import Video

class VideoForm(ModelForm):
    class Meta:
        model = Video
        
        fields = ("video_link",)
from django import forms

class VideoForm(forms.Form):
    
    video_link = forms.CharField(label="Video", max_length=150)
    class Meta:
        widgets = {
            "video_link": forms.TextInput(attrs={"class": "form-control"}),
        }
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import VideoForm

def index(request):
    context = {}
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            vid_link = form.cleaned_data["video_link"]
            form.save()
            
        return HttpResponse("Hello, world. You're at the polls index.")
    else:
        form = VideoForm()
    
    context["form"] = form
    return render(request, "index.html", context)
from django.shortcuts import render, redirect
from django.http import HttpResponse

from .forms import VideoForm
from .utils import *

def index(request):
    # delete_temp_files()
    context = {}
    if request.method == "POST":
        form = VideoForm(request.POST)
        if form.is_valid():
            vid_link = form.cleaned_data["video_link"]
            
            processed_video, segments = process_video(vid_link)
            context["video"] = processed_video
            context["segments"] = segments
            context["seg_exists"] = True
            
        return render(request, "video/index.html", context)
    else:
        form = VideoForm()
    context["form"] = form
    context["seg_exists"] = False
    return render(request, "video/index.html", context)
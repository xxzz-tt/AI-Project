from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import glob
from translatepy import Translator
import os
import pandas as pd
import wave

def download_video(vid_link):
    isValidLink = False
    # download video in mp4
    try:
        yt = YouTube(vid_link)
    except:
        return None, isValidLink, "This is not a valid YouTube link!"
    video_stream = yt.streams.filter(
        progressive=True, file_extension="mp4"
    ).first()
    filename = "UIFiles/" + yt.title + ".mp4"
    video_stream.download("UIFiles/", yt.title + ".mp4")
    isValidLink = True

    return filename
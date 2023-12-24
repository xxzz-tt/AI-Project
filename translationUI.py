import streamlit as st
import whisper
from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import glob
from translatepy import Translator
import os
import pandas as pd
from TTS.api import TTS
import wave

@st.cache_resource
def load_whisper_model():
    model = whisper.load_model("base")
    return model

@st.cache_resource
def load_audio_model():
    device = "cpu"
    tts = TTS(model_name="tts_models/fr/mai/tacotron2-DDC").to(device)
    return tts

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

    return filename, isValidLink, "Valid Link"

def vid_audio_to_text(vid, model):
    # separate audio from video in mp4 format
    videoclip = VideoFileClip(vid)
    audioclip = videoclip.audio
    file_name = vid.replace(".mp4", ".mp3")
    audioclip.write_audiofile(file_name)
    
    # convert audio clip to text
    result = model.transcribe(file_name)
    text = result["text"]
    segments = result["segments"]
    segments_df = pd.DataFrame(segments, columns=['start', 'end', 'text'])
    
    segments_df.columns = ['Timestamp', 'End_Timestamp', 'Original Text']
    
    return file_name, text, segments_df

def translate(text, language="French"):
    translator = Translator()
    translated = translator.translate(text, language)

    return translated.result

def convert_french_to_audio(original_text, tts_model, output_path=""):
    tts_model.tts_to_file(original_text, file_path=output_path)
        
def delete_temp_file(fpath):
    if os.path.exists(fpath):
        os.remove(fpath)
        
def change_audio_speed(audio_fname, scale_factor):
    oa = wave.open(audio_fname, 'rb')
    rate = oa.getframerate()
    signal = oa.readframes(-1)
    
    new_fname = audio_fname.replace('.wav', '_speed.wav')
    new_aud = wave.open(new_fname, 'wb')
    new_aud.setnchannels(1)
    new_aud.setsampwidth(2)
    new_aud.setframerate(rate * scale_factor)
    new_aud.writeframes(signal)
    new_aud.close()
    
    return new_fname
        
def add_subtitles_and_translation_to_movie(subs_df, translated, vid_fname):
    segs = subs_df.values.tolist()
    subs = []
    for start, end, text in segs:
        subs.append(((start, end), text))
        
    video = VideoFileClip(vid_fname)
    generator = lambda txt: TextClip(txt, font='Arial', fontsize=16, color='white', method='caption', align='south', size=video.size)
        
    subtitles = SubtitlesClip(subs, generator)
    audio_fr_name = vid_fname.replace('.mp4', '_subs.wav')
    convert_french_to_audio(translated, tts, audio_fr_name)
    
    audio_fr = AudioFileClip(audio_fr_name)
    new_audio_fr = change_audio_speed(audio_fr_name, audio_fr.duration/video.duration)
    audio_fr = AudioFileClip(new_audio_fr)
    
    video_fr = video.set_audio(audio_fr)
    
    result = CompositeVideoClip([video_fr, subtitles.set_pos(('center','bottom'))])
    sub_vid_fname = vid_fname.replace(".mp4", "_subs.mp4")
    result.write_videofile(sub_vid_fname, fps=video_fr.fps)
    return sub_vid_fname, audio_fr_name, new_audio_fr

st.title("Translate YouTube subtitles from English to French")

form = st.form(key='my_form')
vid_link = form.text_input("Select a YouTube Video with English Captions", placeholder="Enter full URL")
submitted = submit_button = form.form_submit_button(label='Submit')
    
if submitted:
    vid_fname, isValidLink, captions = download_video(vid_link)
    if not isValidLink:
        st.write(captions)
    else:
        model = load_whisper_model()
        tts = load_audio_model()
        
        st.write("Processing video... This might take more than 10 minutes.")
        audio_fname, audio_text, segments_df = vid_audio_to_text(vid_fname, model)
        
        # subtitles with timestamp
        segments_df['Translated Text'] = segments_df['Original Text'].apply((lambda x: translate(x)))
        translated_audio_text = translate(audio_text)
        
        sub_vid_fname, audio_fr_name, new_audio_fr = add_subtitles_and_translation_to_movie(segments_df[['Timestamp', 'End_Timestamp', 'Translated Text']], translated_audio_text, vid_fname)
        
        st.video(sub_vid_fname)
        
        segments_df['Timestamp'] = segments_df['Timestamp'].map(lambda x: '{:02}:{:02}:{:02.2f}'.format(int(x//3600), int(x%3600//60), x%60))
        del segments_df['End_Timestamp']
        
        st.table(segments_df.set_index(segments_df.columns[0]))
        
    delete_temp_file(vid_fname)
    delete_temp_file(audio_fname)
    delete_temp_file(sub_vid_fname)
    delete_temp_file(audio_fr_name)
    delete_temp_file(new_audio_fr)
    

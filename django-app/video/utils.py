from pytube import YouTube
from urllib.parse import urlparse, parse_qs
from moviepy.editor import *
from moviepy.video.tools.subtitles import SubtitlesClip
import glob
from translatepy import Translator
from TTS.api import TTS
import pandas as pd
import wave
import whisper
import os 

output_dir = "static/video/"

def download_video(vid_link):
    
    yt = YouTube(vid_link)
    video_stream = yt.streams.filter(
        progressive=True, file_extension="mp4"
    ).first()
    
    filename = yt.title + ".mp4"
    video_stream.download(output_dir, filename)

    return filename

def vid_audio_to_text(vid):
    # separate audio from video in mp4 format
    videoclip = VideoFileClip(output_dir + vid)
    audioclip = videoclip.audio
    filename = vid.replace(".mp4", ".mp3")
    audioclip.write_audiofile(output_dir + filename)
    
    # convert audio clip to text
    model = whisper.load_model("base")
    result = model.transcribe(output_dir + filename)
    text = result["text"]
    segments = result["segments"]
    segments_df = pd.DataFrame(segments, columns=['start', 'end', 'text'])
    
    segments_df.columns = ['Timestamp', 'End_Timestamp', 'Original']
    
    return filename, text, segments_df

def translate(text, language="French"):
    translator = Translator()
    translated = translator.translate(text, language)

    return translated.result

def convert_french_to_audio(text, output_path=""):
    device = "cpu"
    tts = TTS(model_name="tts_models/fr/mai/tacotron2-DDC").to(device)
    tts.tts_to_file(text, file_path=output_dir + output_path)
    
def change_audio_speed(audio_fname, scale_factor):
    oa = wave.open(output_dir+audio_fname, 'rb')
    rate = oa.getframerate()
    signal = oa.readframes(-1)
    
    new_fname = audio_fname.replace('.wav', '_speed.wav')
    new_aud = wave.open(output_dir+new_fname, 'wb')
    new_aud.setnchannels(1)
    new_aud.setsampwidth(2)
    new_aud.setframerate(rate * scale_factor)
    new_aud.writeframes(signal)
    new_aud.close()
    
    return new_fname

def add_subtitles_and_translation_to_movie(subs_df, vid_fname, audio_fr_name):
    segs = subs_df.values.tolist()
    subs = []
    for start, end, text in segs:
        subs.append(((start, end), text))
        
    video = VideoFileClip(output_dir + vid_fname)
    generator = lambda txt: TextClip(txt, font='Nimbus-Sans', fontsize=16, color='white', method='caption', align='south', size=video.size)
        
    subtitles = SubtitlesClip(subs, generator)
    
    audio_fr = AudioFileClip(output_dir + audio_fr_name)
    new_audio_fr = change_audio_speed(audio_fr_name, audio_fr.duration/video.duration)
    audio_fr = AudioFileClip(output_dir + new_audio_fr)
    
    video_fr = video.set_audio(audio_fr)
    
    result = CompositeVideoClip([video_fr, subtitles.set_pos(('center','bottom'))])
    
    sub_vid_fname = vid_fname.replace(".mp4", "_subs.mp4")
    result.write_videofile(output_dir + sub_vid_fname, fps=video_fr.fps)
    
    return sub_vid_fname, new_audio_fr

def delete_temp_files():
    os.system("rm -rf " + output_dir)
        
def process_video(vid_link):
    vid_filename = download_video(vid_link)
    
    aud_filename, text, segments_df = vid_audio_to_text(vid_filename)
    
    segments_df['Translated'] = segments_df['Original'].apply((lambda x: translate(x)))
        
    translated = translate(text)
    aud_fr_filename = aud_filename.replace('.mp3', '_subs.wav')
    convert_french_to_audio(text, aud_fr_filename)
    
    sub_vid_fname, new_audio_fr = add_subtitles_and_translation_to_movie(segments_df[['Timestamp', 'End_Timestamp', 'Translated']], vid_filename, aud_fr_filename)
    
    segments_df['Timestamp'] = segments_df['Timestamp'].map(lambda x: '{:02}:{:02}:{:02.2f}'.format(int(x//3600), int(x%3600//60), x%60))
    del segments_df['End_Timestamp']
    
    print(segments_df)
    return "video/" + sub_vid_fname, segments_df
    
from pytube import YouTube
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api.formatters import JSONFormatter
from urllib.parse import urlparse, parse_qs


def download_video(videos_file):
    with open(videos_file) as f:
        videos = f.readlines()
        for vid_link in videos:
            # download video in mp4
            yt = YouTube(vid_link)
            video_stream = yt.streams.filter(
                progressive=True, file_extension="mp4"
            ).first()
            video_stream.download("Videos/", yt.title + ".mp4")

            # download english captions
            query_params = parse_qs(urlparse(vid_link).query)
            vid_id = query_params["v"][0]

            captions = YouTubeTranscriptApi.get_transcript(vid_id, languages=["en"])
            formatter = JSONFormatter()
            formatted_captions = formatter.format_transcript(captions)

            with open("Captions/" + yt.title + ".json", "w", encoding="utf-8") as f:
                f.write(formatted_captions)


if __name__ == "__main__":
    # download_video("video_links.txt")
    t = YouTubeTranscriptApi.get_transcript("bNKdlnoAqIs", languages=["en"])
    formatter = JSONFormatter()
    formatted_captions = formatter.format_transcript(t)
    print(t)

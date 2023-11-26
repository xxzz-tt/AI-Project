# AI-Project

Contributor: Xuan Zhi Tan\
Net ID: xt2255

## Data
Video data used in this project is taken from [60 Minutes](https://www.youtube.com/@60minutes). They can be found [here](https://huggingface.co/datasets/xuanzz/VideoCaptions/tree/main) together with their corresponding captions. 

## How to run

### Milestone 1

1. python video_download.py

The program will download all YouTube videos specified in `video_links.txt` and their English captions to `Videos/` and `Captions/` folders respectively.

### Milestone 2

1. Run functions in milestone-2.ipynb to separate audio from the specified video and convert the audio to text.

### Milestone 3
1. The function will translate each text file in the specified input folder path from English to French (default). 

### Milestone 4
1. The function takes a French text file as input and convert it to audio. 
# Web of videos #
## Overview ##
One of the most popular websites for hosting videos is youtube. Institutions have made tremendous contributions in making high quality educational videos available to anyone. 
However these information still remains somewhat scattered. Youtube is good at suggesting videos of the same genre, however for educational purpose videos it still lacks a more fine graned content matching in order to supplement the currently playing video

The project aims to realize a prototype of "web of videos." It will link to other videos of similar content to the currently playing video.
Moreover, instead of finding similar videos for the entire video, it will suggest similar videos for each video segment. 
It also annotates each similar video with descriptions to help the user select the most relevent link
If a link description is not available it will simply display "None"

## Website demo ##
Please use the following resources for a step by step demo
[web of videos website](http://cindyst2.web.illinois.edu/wov)
[web of videos demo]

## Installation Instructions ##
The following are the instructions to deploy the source code in your local machine

### Anaconda Setup Enviornment ###
Clone the repo
```bash
git clone https://github.com/noya/web-of-videos.git
cd web-of-videos
unzip data.zip
```
Create conda enviornment
```bash
conda create -n myenv python=3.6
source activate myenv
pip install -r requirements.txt
```
Run gunicorn in your local enviornment

#### For Window Users ####
```bash
# Install superset
pip install superset

# Create an admin user (you will be prompted to set a username, first and last name before setting a password)
fabmanager create-admin --app superset

# Initialize the database
cd C:\venv\Scripts\ && python superset db upgrade

# Load some data to play with
python superset load_examples

# Create default roles and permissions
python superset init

# To start a development web server on port 8088, use -p to bind to another port
superset runserver -d
```

#### For Linux / MAC Users ####
```bash
gunicorn -w 4 controller:app
```

Play with the website in your local browser
Open any web browser and type in the address localhost:5000

### Testing ###
To test out some of the functionality
```bash
python src/web_of_videos.py
```
This will use the hardcoded url, segment index, and total segments to find similar queries

If you choose the provide parameters on your own, you can try this
```bash
python src/web_of_videos.py [url] [segment_idx] [total_segments]
```
Note that the url must be one of the following playlist from UIUC's text information system course
[UIUC text information system](https://youtu.be/A6NEmoeqUnU?list=PLLssT5z_DsK8Jk8mpFc_RPzn2obhotfDO)
todo: change above to playlist

## Implementation Details ##
The directory structure is as follows

- src
   + download_youtube_files.py
   + web_of_videos.py
- templates
   + web-of-videos.html
- data
   - cmu-nn-nlp
   - stanford-nlp
   - uiuc-text-mining-analytics
   - mit-linear-algebra
   - um-natural-language-processing
   - stanford-conv-nn
   + dataset-full-corpus.txt
   + metadata.dat
   + file.toml
+ config.toml
+ uiuc-textinfo-config.toml
+ controller.py
+ passenger_wsgi.py
+ requirements.txt
+ stopwords.txt

**Back end**

This project chooses metapy as the language processing toolkit. 

download_youtube_files.py downloads youtube playlists and convert it to metapy friendly data format.

web_of_videos.py reads the data created by download_youtube_files.py to create file indexes. It processes periodic requets sent by the web to retrieve similar videos. 
Specifically, it creates a query based on the currently playing video title and video content.
It applies inverse document frequency on the terms so unimportant words such as "the", "we", becomes insignificant. 
After the transformation it then selects the top ? terms to perform the query. 
The query uses BM25 with Rocchio feedback.

**Front end**

wov.py
web-of-video.html displays the videos using youtube IFrame API. It retrieves the video information such as its url and playing progress and send it to web_of_videos.py script.
After receiving the result from web_of_videos.py it displays the vidoes title and description and provide a link to these videos
Note if the video is playing it will send requests to web_of_videos.py every 1 sec. Otherwise if the video is paused/buffering/ etc it will also send a request to update the links.

## Include your own video content ##
If the you plan to include videos of your choice to be part of the database follow these steps:

1. Edit the json file to include the link the the video playlist and the directory name you want the data to be stored.
The data will all be downloaded under data/<directory_name>

2. Run the src/download_youtube_files.py
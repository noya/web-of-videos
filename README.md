# Web of videos #
## Overview ##
The education cost in US has been steadily [rising] (https://nces.ed.gov/fastfacts/display.asp?id=76) while the median household income remains [flat] (https://en.wikipedia.org/wiki/Household_income_in_the_United_States). Accessibility to high quality education becomes a huge issue. 
Thankfully the rise of massive open online course (MOOC) offers an affordable alternative. Popular MOOCs such as Coursera and EdX offers courses from world class univeristy for a small fee. However there are still some downsides with the current online learning method. 
First, the structures of the MOOC platforms is regid and is predefined by the instructor. It does not leverage vast amount of resources on the web. Second, the resources on the web is scattered. It is really hard to browse through all the relevant videos covering a single topic. 
These are the issues that this project aims to address.

The project tries to realize a prototype of "web of videos." It will link videos of similar content to the currently video playlist.
Moreover, instead of finding similar videos for the entire video, it will suggest similar videos for each video segment. 
It also annotates each video with descriptions to help the user select the most relevent link.

## Usage ##
A website demoing this project is hosted here:
[web of videos website](http://cindyst2.web.illinois.edu/wov)

A presentation of this project is hosted here: 
[web of videos demo](https://www.youtube.com/watch?v=IWlzKeD1ttU&feature=youtu.be)

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

#### For Linux / MAC Users ####
Note: Due to some incompatibility between flask and metapy, if you try to run this this website on windows the program will hang
To run the website in your local machine:
```bash
gunicorn -w 4 controller:app
```
The terminal will display which port the website will be running on
Open any web browser and type in the address localhost:<port>

### Testing ###
If the user choose not to host the website on their local machine but want to test out the video search functionality they can do so as follows:
```bash
python src/web_of_videos.py [search_text]
```
This will return related videos using the search_text the user has inputed. 

## Implementation Details ##
The directory structure is as follows

```bash
-src
   +download_youtube_files.py
   +web_of_videos.py
-templates
   +web-of-videos.html
-data
   -cmu-nn-nlp
      +*.en.vtt
   -stanford-nlp
      +*.en.vtt
   -uiuc-text-mining-analytics
      +*.en.vtt
   -mit-linear-algebra
      +*.en.vtt
   -um-natural-language-processing
      +*.en.vtt
   -stanford-conv-nn
      +*.en.vtt
   +dataset-full-corpus.txt
   +metadata.dat
   +file.toml
+config.toml
+controller.py
+passenger_wsgi.py
+requirements.txt
+stopwords.txt
```

There are three main components in this project. The front end html file, web_of_videos.html, the controller, controller.py, and the backend file to process the requests, web_of_videos.py

**web_of_videos.html**

web_of_videos.html displays the videos using youtube IFrame API. It retrieves the video url and playing progress.
Each video is segmented into 3 partitions. Only if the video progresses to different segments (say 0/3 to 1/3) will web_of_videos.html send a request to the controller's getSimVideos to retrieve similar videos. 
After the request has been served, controller.py will return a list of similar videos to web_of_videos.html. web_of_videos.html displays the list of vidoes titles, video descriptions and hyper links to these videos
Note if the video is playing it will send requests to controller.py every 1 sec. Otherwise if the video is paused/buffering/ etc it will also send a request to update the links.

Another functionality of the web_of_videos.html is to take user's input and forward it to controller.py's searchVideos function. This enables the user to directly search for videos. The rest of the functionality is similar to the getSimVideos function.
The only difference is instead of composing the query using the currently playing video information, it compose the query using the user's input.

**controller.py**

The controller acts as a middle man that processes requests to web_of_videos.py's getSimVideos or searchVideos functions. If the request is not approriate it will throw a 400 bad request error.

**web_of_videos.py**

web_of_videos.py reads the data created by download_youtube_files.py to create file indexes. In the getSimVideos function, it processes periodic requets sent by the controller to retrieve similar videos. 
Specifically, it creates a query based on the currently playing video title and video content.
It applies term frequency and inverse document frequency transformation on the terms so unimportant words such as "the", "we", becomes insignificant. 
After the transformation it then selects the top 10 terms to perform the query. 
The query uses BM25 ranker with Rocchio feedback to retrieve similar videos.

As mentioned before, web_of_videos.py also implements another functionality, searchVideos, that takes users's input to search for videos.
Similar to the previous functionality, it uses BM25 ranker and Rocchio feedback to retrieve similar videos. The top ranked video will be played in web_of_videos.html

**download_youtube_files.py**

This project chooses metapy as the language processing toolkit. 
download_youtube_files.py downloads youtube playlists information and convert it to metapy friendly data format.

If the you plan to add additional videos of your choice to be part of the database follow these steps (Note: the video must have either subtitles!):

```bash
# edit the playlist.json file
nano data/playlist.json # or any editor of your choice

# download the content
# The data will be downloaded under data/<directory_name>, where directory_name is specified by the user in playlist.json
python src/download_youtube_files.py

```
If you want to regenerate the entire data base folder, follow these steps:
```bash
mv data data_old
mkdir data
cp data_old/files.toml data
cp data/playlist.json data

# edit data/playlist.json if need be
# download video information
python src/download_youtube_files.py -v # optional -v switch if you want to run it in verbose mode
```


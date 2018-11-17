# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 23:03:31 2018

@author: noyana
"""
import glob
import re
import os
import youtube_dl
from subprocess import call
import subprocess
import json
import warnings
import sys

def get_coursera_files(path, corpus_prefix):
    """
    Use the provided path to cs410 and write the corpus file
    path - path to folder storing data
    """
    # grab all files with en.txt in extension
    files = glob.glob(path + "/*/*/*.en.txt", recursive=True)   

    corpus = open(corpus_prefix + "-full-corpus.txt", "w")
    
    for f in files:
        name = re.sub(r'^.*\\.*[0-9][-|_](.*).en.txt', r'\1', f)
        line = name + " " + f + "\n"
        print(line)
        corpus.write(line)

    

def read_json(json_path):
    with open(json_path) as json_data:
        d = json.load(json_data)
        json_data.close()
        return d

def get_playlistid(d):
    """ 
    extract video playlist id from information file.
    
    Args:
        d - video info file
    Returns:
        playlist_id - video playlist id
    """
    playlist_id = d['playlist_id']
    return playlist_id
    
def get_title(d):
    """ 
    extract video title from information file. If video title contains white spaces convert to '-'
    return key which is the first two strings in the video title
    
    Args:
        d - video info file
    Returns:
        title - video title
        key - first two strings in video title
    """
    title = d['title'].encode('ascii', errors='ignore').decode()
    new_title = re.sub(r'\s', r'-', title)
   
#    key = re.sub(r'(^\S+\s+\S+)\s+.*', r'\1', title)
#    key = re.sub(r'\s', r'-', key)
#    key = re.sub(r':', "", key)
#    key = key + '-'
#   
    return new_title

def get_videoid(d):
    return d['id']

def get_path(video_id, subtitles):
    """ 
    extract video subtitle path from information file.
    
    Args:
        key - key to search for matching subtitle
        subtitles - list of subtitles
    Returns:
        subtitle - A subtitle which contains key phrase. 
    """
    paths = list(filter(lambda subtitle_name : video_id in subtitle_name, subtitles))
    #print("title=", key, ",path", paths)
    if len(paths) != 1:
        warnings.warn("number of paths for video_id " + video_id + " is " + str(len(paths)))
        return None
    
    return paths[0].encode('ascii', errors='ignore').decode()


def get_tags(d):
    """ 
    extract video tags from information file. Convert to a string
    
    Args:
        d - video information
    Returns:
        tags - A list of sentences describing the video
    """
    tags = d['tags']
    concat_tags = ""
    for t in tags:
        # make sure we don't have any non-ascii characters
        t = t.encode('ascii', errors='ignore').decode()
        concat_tags = concat_tags + t + ","
        
    return concat_tags


def get_description(d):
    """ 
    extract video descriotion from information file.
    
    Args:
        d - video information
    Returns:
        description - A short sentence describing the video
    """
    description = d['description']
    description = description.encode('ascii', errors='ignore').decode()

    # will only show no more than 200 characters
    if len(description) > 200:
        description = description[:200]
        description = re.sub(r'(\n|\t|\*)?', "", description)
        
    return description


    
def download_youtube_subtitle(dir_name, playlist_name):
    
    # save previous directory
    prev_dir = os.getcwd()
    
    # change to new directory
    os.chdir(dir_name)
    
    # setup youtube options
    ydl_opts = {
        'skip_download' : True,
        #'allsubtitles' : True,
        'subtitleslangs': ['en'],
        'writesubtitles': True,
        'writeinfojson': True,
        'writeautomaticsub': True
            
    }
    
    # make youtube_dl call
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        ydl.download([playlist_name])
    
    # make sure the subtitle names doesn't have write space
    # if subtitles does have spaces, rename the subtitles
    #fse = sys.getfilesystemencoding()
    subtitles = glob.glob("*.en.vtt")
    
    # need to make sure there's no white spaces in the subtitle names
    new_subtitles = [re.sub(r'\s', r'-', subtitle) for subtitle in subtitles]
    new_subtitles = [s.encode('ascii', errors='ignore').decode() for s in new_subtitles]
    
    # need to make sure there's no non-ascii characters in the subtitle names
    for idx in range(len(new_subtitles)):
        print(subtitles[idx], new_subtitles[idx])
        call(["mv", subtitles[idx], new_subtitles[idx]])
        
    # return to original directory
    os.chdir(prev_dir)
    
def write_youtube_metadata(path, prefix):
    """ 
    write video's corpus-full.txt and metadata.dat
    
    Args:
        path - path containing the subtitles and json files
        prefix - prefix for corpus and metadata file
    Returns:
        None
    """
    # get json files and subtitle files
    jsons = glob.glob(path + "/*.json")
    subtitles = glob.glob(path + "/*.en.vtt")
     
    # open files for writing
    corpus = open(prefix + "-full-corpus.txt", "w")
    metadata = open(prefix + "-metadata.dat", "w")
    
    # loop through each video inforation file
    for j in jsons:
        # read video information
        d = read_json(j)
        assert(d != None)
        
        # extract video title information, convert white spaces to '-'
        title = get_title(d)
         
        # extract video url
        url = d['webpage_url']   
        
        # extract video subtitle path, convert white spaces to '-'
        path = get_path(get_videoid(d), subtitles)
        
        if path == None:
            continue

        # get playlist_id
        playlist_id = get_playlistid(d)
        
        # extract video description
        description = get_description(d)
        #tags = get_tags(d)
        
        # compose the lines we want to write
        corpus_line = title + " " + path + "\n"
        metadata_line = title + "\t" + path + "\t" + url + "\t" + playlist_id + "\t" + description + "\n" 
        
        # write to file
        corpus.write(corpus_line)
        metadata.write(metadata_line)
            
    # close the files
    corpus.close()
    metadata.close()
    
        
def get_youtube_files(dir_name, playlist_name, skip_download=False):
    prev_dir = os.getcwd()
    os.chdir("data")
    if not os.path.exists(dir_name):
        call(["mkdir", dir_name])
    
    if not skip_download:
        download_youtube_subtitle(dir_name, playlist_name)
    write_youtube_metadata(dir_name, dir_name)
    os.chdir(prev_dir)
    
def get_stanford_files():
    os.chdir("data/Stanford_MachineLearning/materials/aimlcs229/transcripts")
    
    # grab all files with en.txt in extension
    files = glob.glob("*.pdf", recursive=True)   
    
    for f in files:
        print("Converting", f)
        call(["pdftotext", f])
    
def file_len(file_name):
    p = subprocess.Popen(['wc', '-l', file_name], stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def append_file(full_corpus, file_list, postfix):
    """ Append new file content to filename"""
    # open corpus file for writing
    fullcorpus =  open(full_corpus, "w+")
    line_cnt = 0

    # open each file in file_list 
    for file in file_list:
        print(file['dir_name'])
        filename = file['dir_name'] + postfix
        corpus = open(filename)
        
        # write each line in corpus to fullcorpus
        for line in corpus:
            fullcorpus.write(line)
            line_cnt += 1
            
        corpus.close()
    
    fullcorpus.close()
    
    # return total number of lines written
    return line_cnt
    
def write_corpus(full_corpus, full_metadata, dir_name, file_list):
    """ write contents from each file in corpus_list to corpus_name file
    write contents in each file in metadata_list to metadata_name
    Note the number of lines corpus and metadata must match
    Args:
            full_corpus - file name which will contain all the corpus content
            full_metadata - file name which will contain all the corpus metadata
            dir_name - directory name which contains all the files specified in file_list
            file_list - files containing all the courses
    """
    # store the current directory. Change to specified directory
    prev_dir = os.getcwd()
    os.chdir(dir_name)
    
    # check before we start anything, the two input files have the same number of lines
    assert(file_len(full_corpus) == file_len(full_metadata))
    
    # open corpus file for writing
    corpus_postfix = "-full-corpus.txt"
    corpus_cnt = append_file(full_corpus, file_list, corpus_postfix)

    # open metadata file for writing
    metadata_postfix = "-metadata.dat"
    metadata_cnt = append_file(full_metadata, file_list, metadata_postfix)           
    
    # move back to previous directory
    os.chdir(prev_dir)
    
    assert(corpus_cnt == metadata_cnt)
    
if __name__ == '__main__':  
    
    playlists = [
        {
                "dir_name":"cmu-nn-nlp",
                "playlist_name" : "https://www.youtube.com/playlist?list=PL8PYTP1V4I8ABXzdqtOpB_eqBlVAz_xPT"
        },
        {
                "dir_name" :"stanford-nlp",
                "playlist_name" : "https://www.youtube.com/playlist?list=PLoROMvodv4rOFZnDyrlW3-nI7tMLtmiJZ"
        },
        {
                "dir_name" : "stanford-conv-nn",
                "playlist_name" : "https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv"
    
        },
        {
                "dir_name" : "mit-linear-algebra",
                "playlist_name" : "https://www.youtube.com/playlist?list=PLE7DDD91010BC51F8"
    
        },
        {
                "dir_name" : "um-natural-language-processing",
                "playlist_name" : "https://www.youtube.com/playlist?list=PLLssT5z_DsK8BdawOVCCaTCO99Ya58ryR"
        },
        {
                "dir_name" : "uiuc-text-mining-analytics",
                "playlist_name" : "https://www.youtube.com/playlist?list=PLLssT5z_DsK8Xwnh_0bjN4KNT81bekvtt"
        },
    
    ]
    #get_youtube_files(playlists[0]['dir_name'], playlists[0]['playlist_name'], skip_download=True)
    for playlist in playlists:
        print(playlist['dir_name'], ":", playlist['playlist_name'])
        get_youtube_files(playlist['dir_name'], playlist['playlist_name'])
        # testing 
    

        
    #get_stanford_files()
    #standord_nlp_playlist = "https://www.youtube.com/playlist?list=PL3FW7Lu3i5Jsnh1rnUwq_TcylNr7EkRe6"
    #stanford_path = "materials\aimlcs229\transcripts"    
    #videos = get_youtube_files("https://www.youtube.com/playlist?list=PL3FW7Lu3i5Jsnh1rnUwq_TcylNr7EkRe6")
    #post_process_youtube_files("stanford-nlp", videos, "stanford-nlp")
    
    #playlist_name = "https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv"
    #videos = get_youtube_metadata(playlist_name)
    #post_process_youtube_files("stanford-nlp", videos, "stanford-nlp")
    #res = download_youtube_subtitle(dir_name, playlist_name)
    #write_youtube_metadata(dir_name, dir_name)


    
    full_corpus = "dataset-full-corpus.txt"
    full_metadata = "metadata.dat"
    
#    file_list = ["data/uiuc-text-mining-analytics",
#                 "data/um-natural-language-processing",
#                 "data/stanford-conv-nn",
#                 "data/stanford-nlp"]
    

    write_corpus(full_corpus, full_metadata, "data", playlists)

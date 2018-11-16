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

    
def download_youtube_subtitle(dir_name, playlist_name):
    
    # save previous directory
    prev_dir = os.getcwd()
    
    # change to new directory
    os.chdir(dir_name)
    
    # setup youtube options
    ydl_opts = {
        'skip_download' : True,
        'allsubtitles' : True,
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
    

def read_json(json_path):
    with open(json_path) as json_data:
        d = json.load(json_data)
        json_data.close()
        return d

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
   
    key = re.sub(r'(^\S+\s+\S+)\s+.*', r'\1', title)
    key = re.sub(r'\s', r'-', key)
    key = key + '-'
    
    return new_title, key

def get_path(key, subtitles):
    """ 
    extract video subtitle path from information file.
    
    Args:
        key - key to search for matching subtitle
        subtitles - list of subtitles
    Returns:
        subtitle - A subtitle which contains key phrase. 
    """
    paths = list(filter(lambda subtitle_name : key in subtitle_name, subtitles))
    #print("title=", key, ",path", paths)
    if len(paths) != 1:
        warnings.warn("number of paths for key " + key + " is " + str(len(paths)))
        return None
    
    return paths[0].encode('ascii', errors='ignore').decode()

def get_description(d):
    """ 
    extract video descriotion from information file.
    
    Args:
        d - video information
    Returns:
        description - A short sentence describing the video
    """
    description = d['description']
    
    # will only show no more than 200 characters
    if len(description) > 200:
        description = description[:200]
        description = re.sub(r'\n', "", description)
        
    return description
        
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
    os.getcwd()
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
        title, key = get_title(d)
        print(key)
        
        # extract video url
        url = d['webpage_url']   
        
        # extract video subtitle path, convert white spaces to '-'
        path = get_path(key, subtitles)
        
        if path == None:
            continue

        # extract video description
        description = get_description(d)

        # compose the lines we want to write
        corpus_line = title + " " + path + "\n"
        metadata_line = title + "\t" + path + "\t" + url + "\t" + description + "\n" 
        
        # write to file
        corpus.write(corpus_line)
        metadata.write(metadata_line)
            
    # close the files
    corpus.close()
    metadata.close()
    
        
def get_youtube_files(dir_name, playlist_name):
    #call(["mkdir", dir_name])
    download_youtube_subtitle(dir_name, playlist_name)
    write_youtube_metadata(dir_name, dir_name)
    
def get_stanford_files():
    os.chdir("data/Stanford_MachineLearning/materials/aimlcs229/transcripts")
    
    # grab all files with en.txt in extension
    files = glob.glob("*.pdf", recursive=True)   
    
    for f in files:
        print("Converting", f)
        call(["pdftotext", f])
    


def create_corpus():
    os.chdir("data")
    get_coursera_files("cs-410", "cs-410")
    get_coursera_files("language-processing", "language-processing")
    
if __name__ == '__main__':
    #path = sys.argv[1]
    #corpus_prefix = sys.argv[2]
    #get_coursera_files(path, corpus_prefix)
    os.chdir("data")
    #get_stanford_files()
    #standord_nlp_playlist = "https://www.youtube.com/playlist?list=PL3FW7Lu3i5Jsnh1rnUwq_TcylNr7EkRe6"
    #stanford_path = "materials\aimlcs229\transcripts"    
    #videos = get_youtube_files("https://www.youtube.com/playlist?list=PL3FW7Lu3i5Jsnh1rnUwq_TcylNr7EkRe6")
    #post_process_youtube_files("stanford-nlp", videos, "stanford-nlp")
    
    dir_name = "stanford-conv-nn"
    playlist_name = "https://www.youtube.com/playlist?list=PL3FW7Lu3i5JvHM8ljYj-zLfQRF3EO8sYv"
    #videos = get_youtube_metadata(playlist_name)
    #post_process_youtube_files("stanford-nlp", videos, "stanford-nlp")
    #res = download_youtube_subtitle(dir_name, playlist_name)
    #write_youtube_metadata(dir_name, dir_name)

    dir_name = "um-natural-language-processing"
    playlist_name = "https://www.youtube.com/playlist?list=PLLssT5z_DsK8BdawOVCCaTCO99Ya58ryR"
    get_youtube_files(dir_name, playlist_name)
    #write_youtube_metadata(dir_name, dir_name)

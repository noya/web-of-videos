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
import shutil
import metapy
import subprocess
import json
import warnings
import sys


##################################################
# helper functions for downloading course data
##################################################

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
    if len(description) > 250:
        # restrict the content count
        description = description[:250]
        
    # if there's new line than only capture current line
    description = re.sub(r'\n', r' ', description)
    description = re.sub(r'(\t)?', "", description)

    if description == "":
        description = "None"
    
    return description


##################################################
# end of helper functions for downloading course data
##################################################
    
def download_subtitles(dir_name, playlist_name):
    """
    download all the english subtitles in playlist
    Args:
        dir_name: directory in which the subtitles will be downloaded
        playlist_name: playlist name
    Returns:
        None
    """
    # save previous directory
    prev_dir = os.getcwd()
    
    # change to new directory
    os.chdir(dir_name)
    
    # setup youtube_dl options
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
    
    # check subtitle names
    # substitute white space with hyphen in subtitles
    subtitles = glob.glob("*.en.vtt")
    new_subtitles = [re.sub(r'\s', r'-', subtitle) for subtitle in subtitles]
    
    # remove non-ascii characters
    new_subtitles = [s.encode('ascii', errors='ignore').decode() for s in new_subtitles]
    
    # rename the subtitle files
    for idx in range(len(new_subtitles)):
        print(subtitles[idx], new_subtitles[idx])
        call(["mv", subtitles[idx], new_subtitles[idx]])
        
    # return to original directory
    os.chdir(prev_dir)
    
def test_idx(config_name):
    # load config.file
    fwd_idx = metapy.index.make_forward_index(config_name)
    
    # make a few calls
    print(fwd_idx.num_docs())
    print(fwd_idx.unique_terms())
    print(fwd_idx.metadata(0).get("title"))
    print(fwd_idx.metadata(0).get("path"))
    print(fwd_idx.metadata(0).get("url"))
    print(fwd_idx.metadata(0).get("description"))
    
def test_metapy_files(dir_name, prefix):
    """
    todo: need to fetch the files from path
    The test 
    1. Remove test-idx directory if it exists
    2. rename metapy files so that the files we want to test gets loaded
    2. Load metapy files
    3. Run some tests, make sure there are no errors
    """
    
    # check if test-idx exists
    print("testing", prefix)
    if os.path.exists("idx_orig"):
       shutil.rmtree("idx_orig")
        
    if os.path.exists("idx"):
        os.rename("idx", "idx_orig")
        
    # copy corpus file
    # todo check if dataset and prefix are the same
    if os.path.isfile("data/dataset-full-corpus.txt.orig"):
        os.remove("data/dataset-full-corpus.txt.orig")
    if os.path.isfile("data/dataset-full-corpus.txt"):
        os.rename("data/dataset-full-corpus.txt", "data/dataset-full-corpus.txt.orig")
    shutil.copy("data/"+ dir_name + "/" + prefix + "-full-corpus.txt", "data/dataset-full-corpus.txt")
    
    # copy prefix-metadata.dat to metadata.dat
    if os.path.isfile("data/metadata.dat.orig"):
        os.remove("data/metadata.dat.orig")
    if os.path.isfile("data/metadata.dat"):
        os.rename("data/metadata.dat", "data/metadata.dat.orig")
    shutil.copy("data/" + dir_name + "/" + prefix + "-metadata.dat", "data/metadata.dat")
    
    print("testing index")
    test_idx('test-config.toml')

    # restore to previous state
    shutil.rmtree("idx")
    if os.path.exists("idx_orig"):
        os.rename("idx_orig", "idx")
        
    call(["rm", "-rf", "test-idx"])
    os.remove("data/dataset-full-corpus.txt")
    if os.path.isfile("data/dataset-full-corpus.txt.orig"):
        os.rename("data/dataset-full-corpus.txt.orig", "data/dataset-full-corpus.txt")
    
    os.remove("data/metadata.dat")
    if os.path.isfile("data/metadata.dat.orig"):
        os.rename("data/metadata.dat.orig", "data/metadata.dat")
    
    
def write_metapy_files(path, prefix):
    """ 
    write video's information into metapy format. 
    Specifically prefix-corpus-full.txt and prefix-metadata.dat will be written under path
    
    Args:
        path - path containing the subtitles and json files
        prefix - prefix for corpus and metadata file
    Returns:
        None
    """
    curr_dir = os.getcwd()
    
    # get youtube json files and subtitle files
    jsons = glob.glob(path + "/*.json")
    subtitles = glob.glob(path + "/*.en.vtt")
     
    # open metapy files for writing
    corpus = open(path + "/" + prefix + "-full-corpus.txt", "w")
    metadata = open(path+ "/" + prefix + "-metadata.dat", "w")
    
    # loop through each video information file
    for j in jsons:
        # read video information
        d = read_json(j)
        assert(d != None)
        
        # extract video title information
        title = get_title(d)

        # extract video url
        url = d['webpage_url']   
        
        # extract video subtitle path
        path = get_path(get_videoid(d), subtitles)
        
        # no matching subtitle, continue to next json file
        if path == None:
            continue

        # extract video playlist_id
        playlist_id = get_playlistid(d)
        
        # extract video description
        description = get_description(d)
        
        # compose the lines we want to write
        corpus_line = title + " " + path + "\n"
        metadata_line = title + "\t" + path + "\t" + url + "\t" + playlist_id + "\t" + description + "\n" 
        
        # write to metapy file
        corpus.write(corpus_line)
        metadata.write(metadata_line)
            
    # close metapy files
    corpus.close()
    metadata.close()
    
    
        
def get_course_data(dir_name, playlist_name, skip_download=False):
    prev_dir = os.getcwd()
    os.chdir("data")
    if not os.path.exists(dir_name):
        call(["mkdir", dir_name])
    
    if not skip_download:
        download_subtitles(dir_name, playlist_name)
        
    write_metapy_files(dir_name, dir_name)
    os.chdir(prev_dir)
    
    
def file_len(file_name):
    p = subprocess.Popen(['wc', '-l', file_name], stdout=subprocess.PIPE,
                                                  stderr=subprocess.PIPE)
    result, err = p.communicate()
    if p.returncode != 0:
        raise IOError(err)
    return int(result.strip().split()[0])

def append_file(full_corpus, file_list, postfix, overwrite):
    """ Append new file content to filename"""
    # open corpus file for writing
    opts = "w"
    if not overwrite:
        opts = "w+"
        
    fullcorpus =  open(full_corpus, opts)
    line_cnt = 0

    # open each file in file_list 
    for file in file_list:
        filename = file['dir_name'] + "/" + file['dir_name'] + postfix
        print(filename)
        corpus = open(filename)
        
        # write each line in corpus to fullcorpus
        for line in corpus:
            fullcorpus.write(line)
            line_cnt += 1
            
        corpus.close()
    
    fullcorpus.close()
    
    # return total number of lines written
    return line_cnt
    
def merge_course_data(full_prefix, dir_name, file_list, overwrite=True):
    """ write contents from each file in corpus_list to corpus_name file
    write contents in each file in metadata_list to metadata_name
    Note the number of lines corpus and metadata must match
    Args:
            full_corpus - file name which will contain all the corpus content
            full_metadata - file name which will contain all the corpus metadata
            dir_name - directory name which contains all the files specified in file_list. 
                    Usually dir_name is data
            file_list - files containing all the courses
            overwrite - flag to choose if we want to keep the original content in full-corpus.txt and metadata.dat or append the original file
    """
    # store the current directory. Change to specified directory
    prev_dir = os.getcwd()
    os.chdir(dir_name) 
    
    # open corpus file for writing
    corpus_postfix = "-full-corpus.txt"
    corpus_cnt = append_file(full_prefix + corpus_postfix, file_list, corpus_postfix, overwrite)

    # open metadata file for writing
    metadata_postfix = "-metadata.dat"
    metadata_cnt = append_file(full_prefix + metadata_postfix, file_list, metadata_postfix, overwrite)           
    
    # move back to previous directory
    os.chdir(prev_dir)
    
    assert(corpus_cnt == metadata_cnt)
    
if __name__ == '__main__':  
    
    curr_dir = os.getcwd()
    
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
    
    # download you tube files 
    for playlist in playlists:
        # download and create coursera data files
        get_course_data(playlist['dir_name'], playlist['playlist_name'], skip_download=True)
        # testing : try reading the created coursera data files
        test_metapy_files(playlist['dir_name'], playlist['dir_name'])
    
    # merge all the course data into one file
    full_corpus = "dataset-full-corpus.txt"
    full_metadata = "metadata.dat"
    full_prefix = "merge"
    
    merge_course_data(full_prefix, "data", playlists)
    
    # test merged file
    test_metapy_files("", "merge")
    

    
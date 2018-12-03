# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 19:23:22 2018

@author: noyana
"""

import metapy
import re
import os
import webvtt
    
    
def load_naive_question(txt_fwd_idx, doc_id):
    """ The naive question simply uses the lecture titles to search for matching videos
    The next steps will be to use lecture descriptions or even lecture transcripts for query
    Args:
        idx - uiuc text info document index
        doc_id - document id, matches with lecture number
    Returns:
        query
    """
    query = metapy.index.Document()
    title = txt_fwd_idx.metadata(doc_id).get('title')
    #description = txt_fwd_idx.metadata(doc_id).get('description')
    
    query_content = re.sub(r'(-|\. | \|)', r' ', title)
    query.content(query_content)
    
    return query

def get_docid(videoid_to_docid, video_id):
    """
    Given the video id, return the document ID in the index 
    Args:
        video_id - the unique video id the youtube uses to identify videos
    Returns:
        doc_id - the document id in the index list
    """
    if video_id not in videoid_to_docid:
        print("Video id", video_id, "Not found in UIUC text information playlist")
    
    return videoid_to_docid[video_id]

def get_videoid(url):
    video_id = re.sub(r'https://www.youtube.com/.*v=(\S+).*', r'\1', url)
    video_id = re.sub(r'&list=\S+.*', r'', video_id)
    video_id = re.sub(r'&index=\S+.*', r'', video_id)
    return video_id

def create_videoid_to_docid(txt_fwd_idx):
    """
    Create video_id to doc_id map
    """
    videoid_to_docid = {}
    
    for doc_id in range(txt_fwd_idx.num_docs()):
        url = txt_fwd_idx.metadata(doc_id).get('url')
        video_id = get_videoid(url)
        videoid_to_docid[video_id] = doc_id
        
    return videoid_to_docid
        
    
def proc_title(title):
    proc_title = re.sub(r'-', r' ', title)
    return proc_title
    
def get_related_url(fwd_idx, inv_idx, query, num_results):
    """
    find url similar to query from corpus
    Args:
        fwd_idx: corpus's forward index
        inv_idx: corpus's inverse index
    Return:
        list of document ids
    """
    # find ranker
    bm25 = metapy.index.OkapiBM25(k3 = 600)
    rocchio = metapy.index.Rocchio(fwd_idx, bm25)
    top_docs = rocchio.score(inv_idx, query, num_results=num_results)
    #top_docs = bm25.score(inv_idx, query, num_results=num_results)
    results = []
    for num, (d_id, score) in enumerate(top_docs):
        d = {
            'title' : proc_title(fwd_idx.metadata(d_id).get('title')), 
            'url': fwd_idx.metadata(d_id).get('url')
        }
        print(d)
        #print ("{}\t{}..\n".format(fwd_idx.metadata(d_id).get('title'), fwd_idx.metadata(d_id).get('url')))
        results.append(d)
        
        
    return results
        
def make_index(config):
    """
    config - the config.toml file that specifies dataset
    """
    #print("in make indx", os.getcwd())
    fwd_idx = metapy.index.make_forward_index(config)
    inv_idx = metapy.index.make_inverted_index(config)
    
    return fwd_idx, inv_idx


def get_sec(vtt_time):
    
    # retrieve seconds
    sec_pos = vtt_time.rfind(':')
    sec = vtt_time[sec_pos + 1 : len(vtt_time)-1]
    substr = vtt_time[0:sec_pos]
    
    # retrieve minute
    min_pos = substr.rfind(':')
    minute = vtt_time[min_pos + 1 : sec_pos]
        
    # retrieve hours
    hour = vtt_time[0:min_pos]
        
    total_sec = int(hour) * 60 * 60 + int(minute) * 60 + float(sec)
    return total_sec
    
def load_question(txt_fwd_idx, doc_id, total_segments, segment_idx):
    """
    Args:
        time - fraction between 0 ~ 1, value retrieved by function player.getVideoLoadedFraction()
    """
    assert (segment_idx < total_segments)
    assert (segment_idx >= 0)
    
    envtt_path = txt_fwd_idx.metadata(doc_id).get('path')
    fh = webvtt.read(envtt_path)
    
    # probably should cover > 5 sec
    vtt_per_segment = round(len(fh) / total_segments)

    start_idx = vtt_per_segment * segment_idx
    end_idx = start_idx + vtt_per_segment - 1
    
    content = proc_title(txt_fwd_idx.metadata(doc_id).get('title'))
    
    for idx in range(start_idx, end_idx, 3):
        #print(idx)
        #print(fh[idx].text)
        content = content + fh[idx].text
        
    
    # increment 5
    query = metapy.index.Document()
    query.content(content)

    
    return query
    
    
def get_wov(url, segment_idx, total_segments):
    text_config = 'uiuc-textinfo-config.toml'
    corpus_config = 'config.toml'

    # build indexes 
    fwd_idx, inv_idx = make_index(corpus_config)
    txt_fwd_idx, txt_inv_idx = make_index(text_config)
    videoid_to_docid = create_videoid_to_docid(txt_fwd_idx)

    video_id = get_videoid(url)
    doc_id = get_docid(videoid_to_docid, video_id)
    
    # get query from index
    query = load_question(txt_fwd_idx, doc_id, total_segments, segment_idx)
    print(query.content())
    
    # find video matches
    video_matches = get_related_url(fwd_idx, inv_idx, query, num_results=10)
#    for doc_id in video_matches:
#        print(fwd_idx.metadata(doc_id).get('title'), fwd_idx.metadata(doc_id).get('url'))
    return video_matches

def get_test():
    return "happy string\n"

if __name__ == '__main__':  
    url = 'https://www.youtube.com/watch?v=uzYxh7iGCIM&index=5&list=PLLssT5z_DsK8Jk8mpFc_RPzn2obhotfDO'
    #url = 'https://www.youtube.com/watch?v=z4UbVNRnZM4&list=PLLssT5z_DsK8Jk8mpFc_RPzn2obhotfDO&index=22'
    results = get_wov(url, 1, 5)
    
# -*- coding: utf-8 -*-
"""
Created on Thu Nov  1 19:23:22 2018

@author: noyana
"""

import metapy
import re
import webvtt
import math
    
def load_naive_question(txt_fwd_idx, doc_id):
    """ The naive question simply uses the lecture titles to search for matching videos
    The next steps will be to use lecture descriptions or even lecture transcripts for query
    Args:
        txt_fwd_idx - uiuc text info document index
        doc_id - document id, matches with lecture number
    Returns:
        query
    """
    query = metapy.index.Document()
    title = txt_fwd_idx.metadata(doc_id).get('title')
    
    query_content = re.sub(r'(-|\. | \|)', r' ', title)
    query.content(query_content)
    
    return query

def get_docid(videoid_to_docid, video_id):
    """
    Given the video id, return the document ID in the index 
    Args:
        videoid_to_docid - A mapping of UIUC playlist's video ids to doc_id 
        video_id - unique video id the youtube uses to identify videos
    Returns:
        doc_id - the document id in the index list
    """
    if video_id not in videoid_to_docid:
        print("Video id", video_id, "Not found in UIUC text information playlist")
    
    return videoid_to_docid[video_id]

def get_videoid(url):
    """
    Given a youtube URL, retrieve the video id
    Args:
        url - youtube url 
    Returns:
        video_id -  unique video id the youtube uses to identify videos
    """
    video_id = re.sub(r'https://www.youtube.com/.*v=(\S+).*', r'\1', url)
    video_id = re.sub(r'&list=\S+.*', r'', video_id)
    video_id = re.sub(r'&index=\S+.*', r'', video_id)
    return video_id

def create_videoid_to_docid(txt_fwd_idx):
    """
    Create video_id to doc_id map with the UIUC's video playlist
    Args:
        txt_fwd_idx - UIUC's forwraded index
    Returns:
        mapping of video id to doc id
    """
    videoid_to_docid = {}
    
    for doc_id in range(txt_fwd_idx.num_docs()):
        url = txt_fwd_idx.metadata(doc_id).get('url')
        video_id = get_videoid(url)
        videoid_to_docid[video_id] = doc_id
        
    return videoid_to_docid
        
    
def proc_title(title):
    """
    Given a string, replace all the '-' with space
    Args:
        title - video title
    Returns:
        proc_title - processed title, replaced '-' with spaces
    """
    proc_title = re.sub(r'-', r' ', title)
    return proc_title
    
def get_related_url(fwd_idx, inv_idx, query, num_results):
    """
    find similar videos similar 
    Args:
        fwd_idx - corpus's forward index
        inv_idx - corpus's inverse index
        query - query to retrieve similar videos
        num_results - number of similar videos the function should retrieve
    Return:
        results - list of video title and urls
    """
    # find ranker
    bm25 = metapy.index.OkapiBM25(k3 = 600)
    rocchio = metapy.index.Rocchio(fwd_idx, bm25)
    top_docs = rocchio.score(inv_idx, query, num_results=num_results)

    results = []
    for num, (d_id, score) in enumerate(top_docs):
        d = {
            'title' : proc_title(fwd_idx.metadata(d_id).get('title')), 
            'url': fwd_idx.metadata(d_id).get('url')
        }
        print(d)
        results.append(d)
        
        
    return results
        
def make_index(config):
    """
    Given a config file, make forward and inverted index
    Args:
        config - the config.toml file that specifies dataset
    Returns:
        fwd_idx - forwarded index
        inv_idx - inverted index
    """
    fwd_idx = metapy.index.make_forward_index(config)
    inv_idx = metapy.index.make_inverted_index(config)
    
    return fwd_idx, inv_idx


def get_sec(vtt_time):
    """
    """
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
    
def get_cnt(element):
    return element[1]

def load_question(txt_fwd_idx, inv_idx, doc_id, total_segments, segment_idx, title_mult = 1, num_terms = 10):
    """
    Use the current playing video to generate query. The query is generated using a segment of the video's content.
    The particular segment is identified by the video playing progress. 
    Args:
        txt_fwd_idx - UIUC's farwarded index
        inv_idx - Corpus's inverse index
        doc_id - the doc_id of the current playing video 
        total_segments - total number of segments we want to partition the video 
        segment_idx - segment index of the current video
        title_mult - title multiplier. Determines how much weight we should place on the title. 
        num_terms - limit the number of terms we want to fit in a query
    Returns:
        query - the video query vector
    """
    assert (segment_idx < total_segments)
    assert (segment_idx >= 0)
    
    envtt_path = txt_fwd_idx.metadata(doc_id).get('path')
    fh = webvtt.read(envtt_path)
    
    # calculate how many vtts per segment
    vtt_per_segment = round(len(fh) / total_segments)

    # calculate the start and end vtt (video transcript) index for segment of interest
    start_idx = vtt_per_segment * segment_idx
    end_idx = start_idx + vtt_per_segment - 1
    
    # retrieve current video title
    title = proc_title(txt_fwd_idx.metadata(doc_id).get('title')) 
    content = title * title_mult
    
    # retrieve vtt content from the segment in interest
    for idx in range(start_idx, end_idx, 3):
        content = content + ' ' +  fh[idx].text
        
    # Generate query vector using video segment content
    doc = metapy.index.Document()
    doc.content(content)

    # tokenize query
    qvec = txt_fwd_idx.tokenize(doc)
    
    # use inverse document frequency to weed out unimportant words
    qvec_list = []
    
    for term_id, term_cnt in qvec:
        term = txt_fwd_idx.term_text(term_id)
        inv_term_id = inv_idx.get_term_id(term)
        doc_freq = inv_idx.doc_freq(inv_term_id)
        # todo: check for edge cases when doc_freq = 0
        qvec_list.append((term, term_cnt * math.log((inv_idx.num_docs() + 1)/doc_freq)))
 
    # sort all the query vectors using c(w, d) * log(M/df)
    qvec_list.sort(reverse=True, key=get_cnt)
    
    # only use the top terms in the query
    # the number of terms is specified by num_terms
    query_content = ""
    
    for idx in range(0, num_terms):
        term, cnt = qvec_list[idx]
        query_content = query_content + ' ' + term
        
    # generate query
    # todo: redudant step? already transformed title
    query_mod_content = re.sub(r'_', r' ', query_content)
    query = metapy.index.Document()
    query.content(query_mod_content)
    return query
    
    
def get_wov(url, segment_idx, total_segments):
    """
    Use a video's url and it's playing progress, find similar videos. 
    Args:
        url - video url
        segment_idx - Use segment_idx to represent video's playing progress. Say there are 5 segments, 
                      then segment_idx = 1 represents the video has been playing for 20%
        total_segments - total number of segments to partition the video
    """
    text_config = 'uiuc-textinfo-config.toml'
    corpus_config = 'config.toml'

    # build indexes 
    fwd_idx, inv_idx = make_index(corpus_config)
    txt_fwd_idx, txt_inv_idx = make_index(text_config)
    
    # get videoid to docid mapping
    videoid_to_docid = create_videoid_to_docid(txt_fwd_idx)

    # get video's corresponding video_id and doc_id
    video_id = get_videoid(url)
    doc_id = get_docid(videoid_to_docid, video_id)
    
    # get query from index
    query = load_question(txt_fwd_idx, inv_idx, doc_id, total_segments, segment_idx)

    # find videos using query
    related_videos = get_related_url(fwd_idx, inv_idx, query, num_results=10)
    
    result = {}
    result['related_videos'] = related_videos
    result['query'] = query.content()
    return result


if __name__ == '__main__':  
    url = 'https://www.youtube.com/watch?v=IOgznBexyD0&index=24&list=PLLssT5z_DsK8Jk8mpFc_RPzn2obhotfDO'
    total_segments = 5
    segment_idx = 1
    #print("query:", results['query'])
    results = get_wov(url, 1, 5)
    
    
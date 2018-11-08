# -*- coding: utf-8 -*-
"""
Created on Tue Nov  6 23:03:31 2018

@author: noyana
"""
import glob
import sys
import re
import os

def get_cs410_files(path, corpus_prefix):
    """
    Use the provided path to cs410 and write the corpus file
    path - path to folder storing data
    """
    cwd = os.getcwd()
    os.chdir(path)
    
    # grab all files with en.txt in extension
    files = glob.glob("*/*/*.en.txt", recursive=True)   

    corpus = open(corpus_prefix + "-full-corpus.txt", "w")
    
    for f in files:
        name = re.sub(r'^.*\\.*[0-9][-|_](.*).en.txt', r'\1', f)
        line = name + " " + f + "\n"
        print(line)
        corpus.write(line)
    
    # change back to current directory
    os.chdir(cwd)
        
if __name__ == '__main__':
    path = sys.argv[1]
    corpus_prefix = sys.argv[2]
    get_cs410_files(path, corpus_prefix)

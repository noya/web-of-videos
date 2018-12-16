import sys
from flask import Flask, request, render_template, url_for, redirect, jsonify, abort
import src.web_of_videos as wovpy
from subprocess import check_output, call




app = Flask(__name__)
application = app

@app.route('/')
def show_wov():
    return render_template('web_of_videos.html')
    
@app.route('/getSimVideos', methods=['POST', 'GET'])
def getSimVideos():
    if request.method == "POST":
        url = "none"
        segment_idx = ""
        total_segments = ""
        
        try:
            url = request.json['url']
            segment_idx = request.json['segment_idx']
            total_segments = request.json['total_segments']

        except:
            print ("unexpected error:", sys.exc_info()[0])
            abort(400)
        else:
        
            # build indexes 
            video_matches = wovpy.get_wov(url, segment_idx, total_segments)
            return jsonify(result=video_matches)    
            
    else:
        print("Getting GET requets")
        abort(400)
    
@app.route('/searchVideos', methods=['POST', 'GET'])
def searchVideos():
    if request.method == "POST":
        query = ""
        try:
            query = request.json['query']
            video_matches = wovpy.search_wov(query)
            
            return jsonify(result=video_matches)
        except:
            print ("unexpected error:", sys.exc_info()[0])
            abort(400)
    else:
        print("Getting GET request in search videos")
        abort(400)
        
if __name__ == "__main__":
    app.run(processes=2)
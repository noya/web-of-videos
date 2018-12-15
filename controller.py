import sys
#import portalocker
#sys.path.insert(0, "src")
#from src.hack import fcntl
from flask import Flask, request, render_template, url_for, redirect, jsonify, abort


import json
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
            #video_matches = check_output(["python", "src/web_of_videos.py", url, str(segment_idx), str(total_segments)]) 
            video_matches = wovpy.get_wov(url, segment_idx, total_segments)
            
            print("matches", video_matches)
            related_videos = [
                    {
                            'title' : 'title0',
                            'url' : 'url0',
                            'description' : 'description0'
                    },
                                                {
                            'title' : 'title1',
                            'url' : 'url1',
                            'description' : 'description0'
                    },
                                                                            {
                            'title' : 'title2',
                            'url' : 'url2',
                            'description' : 'description0'
                    },
                                                                                                        {
                            'title' : 'title3',
                            'url' : 'url3',
                            'description' : 'description0'
                    },
                                                                                                                                    {
                            'title' : 'title4',
                            'url' : 'url5',
                            'description' : 'description0'
                    },
                                                                                                                                                                {
                            'title' : 'title6',
                            'url' : 'url7',
                            'description' : 'description0'
                    },
                                                                                                                                                                                            {
                            'title' : 'title8',
                            'url' : 'url9',
                            'description' : 'description0'
                    },

            ]
            #result = {'related_videos' : related_videos}
            #return jsonify(result=result)
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
            #video_matches = check_output(["python", "-c", "from src.web_of_videos import searvhVideos", query]) 
            video_matches = wovpy.search_wov(query)
            
            return jsonify(result=video_matches)
        except:
            print ("unexpected error:", sys.exc_info()[0])
            abort(400)
    else:
        print("Getting GET request in search videos")
        abort(400)
        
if __name__ == "__main__":
    #app.run(debug=True)
    #app.run(threaded=True)
    app.run(processes=2)
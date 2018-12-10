from flask import Flask, request, render_template, url_for, redirect, jsonify
import sys
import json
import web_of_videos as wovpy
from subprocess import check_output

app = Flask(__name__)
application = app

@app.route('/')
def show_wov():
    return render_template('web-of-videos.html')
    
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
            return "url is not a valid key??bad error"
        else:
        
            # build indexes 
             
            video_matches = check_output(["python", "web_of_videos.py", url, str(segment_idx), str(total_segments)]) 

            print("matches", video_matches)
            related_videos = [
                    {
                            'title' : 'title0',
                            'url' : 'url0'
                    },
                                                {
                            'title' : 'title1',
                            'url' : 'url1'
                    },
                                                                            {
                            'title' : 'title2',
                            'url' : 'url2'
                    },
                                                                                                        {
                            'title' : 'title3',
                            'url' : 'url3'
                    },
                                                                                                                                    {
                            'title' : 'title4',
                            'url' : 'url5'
                    },
                                                                                                                                                                {
                            'title' : 'title6',
                            'url' : 'url7'
                    },
                                                                                                                                                                                            {
                            'title' : 'title8',
                            'url' : 'url9'
                    },

            ]
            result = {'related_videos' : related_videos}
            #return jsonify(result=video_matches)    
            #return jsonify(result=video_dl)
            return jsonify(result=result)
    else:
        print("Getting GET requets")
        return "Getting GET requests\n"
        
if __name__ == "__main__":
    app.run(debug=True)
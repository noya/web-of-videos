from flask import Flask, request, render_template, url_for, redirect, jsonify
import sys
import json
import web_of_videos as wovpy
from subprocess import check_output

app = Flask(__name__)
application = app

@app.route('/')
def show_wov():
    #return "hello world\n"
    return render_template('web-of-videos.html')
    
@app.route('/getSimVideos', methods=['POST', 'GET'])
def getSimVideos():
    if request.method == "POST":
        text_config = 'uiuc-textinfo-config.toml'
        corpus_config = 'config.toml'
        url = "none"
        try:
            url = request.json['url']
            #result = wovpy.get_test()
            #return jsonify(result=result)
        except:
            print ("unexpected error:", sys.exc_info()[0])
            return "url is not a valid key??bad error"
        else:
        
            # build indexes 
             
            results = check_output(["python", "web_of_videos.py", url]) 
            video_matches = results.decode("utf-8")
            #video_matches = wovpy.get_wov(url)
#            fwd_idx, inv_idx = wovpy.make_index(corpus_config)
#            txt_fwd_idx, txt_inv_idx = wovpy.make_index(text_config)
#            videoid_to_docid = wovpy.create_videoid_to_docid(txt_fwd_idx)
#            
#        
#            video_id = wovpy.get_videoid(url)
#            print("videoid=",video_id)
#            doc_id = wovpy.get_docid(videoid_to_docid, video_id)
#            print("docid=",doc_id)
#            # get query from index
#            query = wovpy.load_naive_question(txt_fwd_idx, doc_id)
#            print("query", query.content())
#            # find video matches
#            video_matches = wovpy.get_related_url(fwd_idx, inv_idx, query, num_results=10)
            print("matches", video_matches)
            return jsonify(result=video_matches)    
            #return jsonify(result="not hang")
    else:
        print("Getting GET requets")
        return "Getting GET requests\n"
        
if __name__ == "__main__":
    app.run(debug=True)
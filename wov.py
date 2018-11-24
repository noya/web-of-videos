from flask import Flask, request, render_template, url_for, redirect, jsonify
import sys
import json

app = Flask(__name__)
application = app

@app.route('/')
def show_wov():
    #return "hello world\n"
    return render_template('web-of-videos.html')
    
@app.route('/getSimVideos', methods=['POST', 'GET'])
def getSimVideos():
    if request.method == "POST":
        try:
            url = request.json['url']
            #print("url=", url, file=sys.stderr)
            return jsonify(result=str(url))
        except:
            print ("unexpected error:", sys.exc_info()[0])
            return "url is not a valid key??bad error"
    else:
        return "Getting GET requests\n"
        
if __name__ == "__main__":
    app.run(debug=True)
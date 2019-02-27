#!/bin/python
# runTwilioServer.py

from flask import Flask, Response, request, abort, render_template_string, send_from_directory, send_file
import twilio.twiml
 
app = Flask(__name__)

TEMPLATE = '''
<!doctype html>
<title>Hello from Flask</title>
<h1>Hello World!</h1>
'''
 
@app.route("/", methods=['GET', 'POST'])
def index():
    return render_template_string(TEMPLATE)

@app.route('/get_image')
def get_image():
    filename = 'photo.jpg'
    return send_file(filename, mimetype='image/jpg')

def launch_FlaskImgServer():
    app.run(debug=False, host='192.168.1.2')
 
if __name__ == "__main__":
    app.run(debug=True, host='192.168.1.2')


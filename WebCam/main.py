#!/usr/bin/python3
import os

from flask import Flask, send_from_directory, Response
import settings
from WebCam.camdriver import VideoCamera
import json
import cv2

settings = settings.read_setting()
app = Flask(__name__)
global_frame = None
camdriver = None

@app.route("/")
def index():
    # jpg = cv2.imencode(".jpg", camdriver.get_frame()).tobytes()
    return send_from_directory(settings["path_static"], "index.html")


def video_stream():
    global camdriver
    global global_frame

    if camdriver == None:
        camdriver = VideoCamera()
        camdriver.start_record()

    while True:
        frame = camdriver.get_frame()

        if frame != None:
            global_frame = frame
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
        else:
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + global_frame + b'\r\n\r\n')


@app.route("/video")
def video():
    return Response(video_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')
    # return json.dumps(camdriver.get_frame().tolist())

if __name__ == "__main__":
    # global camdriver
    # if camdriver == None:
    #     camdriver = VideoCamera()

    # camdriver.start_record()
    #os.system("/usr/bin/python3 " + settings["path"] + "req.py&")
    app.run(host=settings["host"], port=settings["port"])#, debug=settings["debug"])

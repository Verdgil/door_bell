import datetime
import os

#import numpy as np
import cv2
import time
import math
import settings
import threading


class RecordingThread(threading.Thread):
    def __init__(self, name, camera, settings):
        threading.Thread.__init__(self)
        self.name = name
        self.isRunning = True
        self.settings = settings
        self.cap = camera
        self.fps_num()
        self.fourcc = cv2.VideoWriter_fourcc(*self.settings["output_format"])
        self.out = None

    def fps_num(self):
        start = time.time()
        for i in range(0, 120):
            ret, frame = self.cap.read()
        end = time.time()
        seconds = end - start
        fps1 = 120 / seconds
        fps2 = self.cap.get(cv2.CAP_PROP_FPS)
        # cv2.imencode(".jpg", get_frame())[1].tobytes()
        self.fps = math.floor(min(fps1, fps2))

    def run(self):
        while self.isRunning:
            if not os.path.exists(self.settings["file_prefix"] +
                                  datetime.datetime.now().strftime(
                                      self.settings["date_format"])):
                os.mkdir(self.settings["file_prefix"] +
                         datetime.datetime.now().strftime(
                             self.settings["date_format"]))

            self.out = cv2.VideoWriter(self.settings["file_prefix"] +
                                       datetime.datetime.now().strftime(
                                           self.settings["date_format"]) + "/" +
                                       datetime.datetime.now().strftime(
                                           self.settings["time_format"]) +
                                       self.settings["ext"],
                                       self.fourcc, self.fps, (640, 480))
            for i in range(self.fps*self.settings["rec_time"]):
                try:
                    ret, frame = self.cap.read()
                except:
                    self.isRunning = False
                    break
                else:
                    cv2.putText(frame,
                                datetime.datetime.now().strftime(self.settings["date_format"]) + " " + datetime.datetime.now().strftime(self.settings["time_format"]),
                                (280, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)
                    self.out.write(frame)
            self.out.release()

    def stop(self):
        self.isRunning = False

    def __del__(self):
        self.out.release()


class VideoCamera(object):
    def __init__(self):
        cam_index = self.list_cameras()
        if cam_index["len"] > 0:
            self.cap = cv2.VideoCapture(cam_index["cams_index_array"][0])
        else:
            self.cap = None
        f = open("./../log/log.txt", "a+")
        print("Now cam index:", cam_index, file=f)
        f.close()
        self.is_record = False
        self.out = None
        self.recordingThread = None
        self.settings = settings.read_setting()


    def __del__(self):
        self.cap.release()

    @staticmethod
    def list_cameras():
        devs = os.listdir("/dev")
        cams = []
        for x in devs:
            if x.startswith("video"):
                cams.append(int(x[5:]))
        cams.sort()
        return {"len": len(cams), "cams_index_array": cams}



    def get_frame(self):
        try:
            ret, frame = self.cap.read()
        except:
            self.stop_record()
            self.cap.release()
            cam_index = self.list_cameras()
            if cam_index["len"] > 0:
                self.cap = cv2.VideoCapture(cam_index["cams_index_array"][0])
            else:
                self.cap = None
            self.cap = cv2.VideoCapture(cam_index)
            f = open("./../log/log.txt", "a+")
            print("Now cam index:", cam_index["cams_index_array"][0], file=f)
            f.close()
            self.start_record()
            pass

        if ret:
            cv2.putText(frame,
                        datetime.datetime.now().strftime(
                            self.settings["date_format"]) + " " +
                        datetime.datetime.now().strftime(
                            self.settings["time_format"]),
                        (280, 450), cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 255), 2)

            ret, jpeg = cv2.imencode('.jpg', frame)
            return jpeg.tobytes()

        else:
            return None

    def start_record(self):
        self.is_record = True
        self.recordingThread = RecordingThread("Video Recording Thread", self.cap, self.settings)
        self.recordingThread.start()

    def stop_record(self):
        self.is_record = False

        if self.recordingThread != None:
            self.recordingThread.stop()
        del self.recordingThread
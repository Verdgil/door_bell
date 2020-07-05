import importlib
import inspect
import os
import RPi.GPIO as GPIO
import time
import threading
import subprocess
import datetime


class bell(threading.Thread):
    pull = [GPIO.PUD_OFF, GPIO.PUD_UP, GPIO.PUD_DOWN]
    setting = None
    cam = None

    def __init__(self, settings, cam):
        super().__init__()
        self.cam = cam
        self.setting = settings
        self.setup_GPIO()

    def setup_GPIO(self):
        GPIO.cleanup()
        if self.setting["gpio_mode"] == 1:
            GPIO.setmode(GPIO.BCM)
        else:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.setting["in"], GPIO.IN, pull_up_down=self.pull[self.setting["pull"]])
        if self.setting["need_out"]:
            GPIO.setup(self.setting["out"], GPIO.OUT)
            GPIO.output(self.setting["out"], True)

    def th(self, param, date):
        class_ = getattr(param[0], param[1])
        notify = class_(self.setting, self.cam)
        notify.notify("В дверь звонят в " + str(date))

    def run(self):
        while True:
            signal = GPIO.input(self.setting["in"])
            if signal == 1:
                date = datetime.datetime.now()
                modules = map(lambda mod: (self.setting["notify_prefix"] + "." + mod, mod),
                              self.setting["notifiers"])
                modules = map(lambda x: (importlib.import_module(x[0]), x[1]), modules)
                for i in modules:
                    th = threading.Thread(target=self.th, args=(i, date))
                    th.daemon = True
                    th.start()
                print()
            else:
                time.sleep(0.1)

    def stop(self):
        GPIO.cleanup()

if __name__ == "__main__":
    from settings.settings import settings
    from WebCam.camdriver import VideoCamera

    settings = settings()
    thread = bell(settings, VideoCamera(0, settings))
    thread.daemon = False
    thread.start()
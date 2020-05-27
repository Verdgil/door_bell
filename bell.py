import os
import RPi.GPIO as GPIO
import json
import time
import threading
import subprocess
import datetime
import random
import settings
import lamp
from vk_send import send

pull = [GPIO.PUD_OFF, GPIO.PUD_UP, GPIO.PUD_DOWN]

setting = None
file = open("./log/log.txt", "w")


def th_blink():
    blinker = lamp.lamp()
    blinker.blink()


def setup():
    global setting
    try:
        setting = settings.read_setting()
    except FileNotFoundError:

        setting = {
            "in": 7,
            "out": 0,
            "need_out": False,
            "pull": 2,#0 - GPIO.PUD_OFF, 1 - GPIO.PUD_UP, 2 - GPIO.PUD_DOWN,
            "loop": False,
            "time": 45,
            "gpio_mode": 0
        }
    setting["audio"] = os.listdir("audio")


def setup_GPIO():
    GPIO.cleanup()
    if setting["gpio_mode"] == 1:
        GPIO.setmode(GPIO.BCM)
    else:
        GPIO.setmode(GPIO.BOARD)
    GPIO.setup(setting["in"], GPIO.IN, pull_up_down=pull[setting["pull"]])
    if setting["need_out"]:
        GPIO.setup(setting["out"], GPIO.OUT)
        GPIO.output(setting["out"], True)


def th_audio():
    f = open("/dev/null", "w")
    loop = " -loop 0 " if setting["loop"] else ""
    proc = subprocess.Popen("mplayer \"audio/"
                            + setting["audio"][random.randint(0, len(setting["audio"]) - 1)]
                            + "\" -af volume=10" + loop, shell=True, stdout=f, stderr=f)

def daemon():
    while True:
        signal = GPIO.input(setting["in"])
        if signal == 1:
            #TODO: Отправлять на сервер
            date = datetime.datetime.now()
            try:
                send("В дверь звонят в " + str(date))
            except Exception as e:
                f = open("./log/log.txt", "a+")
                print(e, file=f)
                f.close()

            th_player = threading.Thread(target=th_audio)
            th_player.daemon = True
            th_player.start()
            th_blinker = threading.Thread(target=th_blink)
            th_blinker.daemon = True
            th_blinker.start()
            time.sleep(setting["time"])
            th_player._stop()
            os.system("killall -9 mplayer")
        else:
            time.sleep(0.1)


def run():
    print(os.getcwd(), file=file)
    file.close()
    setup()
    setup_GPIO()
    daemon()


def stop():
    GPIO.cleanup()

if __name__ == "__main__":
    run()
    i = 0
    while True:
        i += 1
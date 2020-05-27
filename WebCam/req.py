import requests
import time
import threading

time.sleep(10)
def th():
    requests.get("http://localhost:8080/video", timeout=100)

ths = threading.Thread(target=th)
time.sleep(10)
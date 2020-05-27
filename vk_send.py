import cv2
import json
import vk
import random
import requests

import settings

from WebCam.camdriver import VideoCamera

settings = settings.read_setting()


def send(message):
    session = vk.Session(access_token=settings["tokken"])
    api = vk.API(session)
    try:
        if VideoCamera().list_cameras()["len"] > 0:
            cam = VideoCamera()
            jpg = cam.get_frame()
            file = open("tempory.jpg", "wb")
            file.write(jpg)
            file.close()
            anw = api.photos.getMessagesUploadServer(v=5.102)
            if "upload_url" in anw.keys():
                url = anw["upload_url"]
                files = {
                    "photo": open("tempory.jpg", "rb")
                }
                upload = json.loads(requests.post(url, files=files).text)
                if "hash" in upload:
                    saved = api.photos.saveMessagesPhoto(server=upload["server"],
                                                         hash=upload["hash"], photo=upload["photo"], v=5.102)
                    if len(saved) > 0 and "date" in saved[0]:
                        attachment_text = "photo" + str(saved[0]["owner_id"]) + "_" + str(saved[0]["id"])
                        api.messages.send(message=message, domain=settings["domain"],
                                          random_id=random.randint(0, 2 ** 64), v=5.102,
                                          attachment=attachment_text)
    except Exception as e:
        api.messages.send(message=message, domain=settings["domain"], random_id=random.randint(0, 2 ** 64), v=5.102)


if __name__ == '__main__':
    s = input("Введите сообщение: ")
    send(s)

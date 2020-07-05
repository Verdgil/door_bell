import json
import vk
import random
import requests

from errors_class.cam_err import cam_not_found
from errors_class.vk_err import vk_upload_err
from notifications.base_notifi import base_notify


class vk_send(base_notify):
    session = None
    api = None
    settings = None
    cam = None

    def __init__(self, settings, cam):
        self.settings = settings
        self.session = vk.Session(access_token=self.settings["tokken"])
        self.api = vk.API(self.session)
        self.cam = cam
        super().__init__(settings, cam)

    def _create_tmp_jpg(self):
        if self.cam is not None:
            jpg = self.cam.get_frame()
            file = open("tempory.jpg", "wb")
            file.write(jpg)
            file.close()
        else:
            raise cam_not_found()

    def _upload_photo(self):
        self._create_tmp_jpg()
        anw = self.api.photos.getMessagesUploadServer(v=5.102)
        if "upload_url" in anw.keys():
            url = anw["upload_url"]
            files = {
                "photo": open("tempory.jpg", "rb")
            }
            upload = json.loads(requests.post(url, files=files).text)
            if "hash" in upload:
                saved = self.api.photos.saveMessagesPhoto(server=upload["server"],
                                                     hash=upload["hash"], photo=upload["photo"], v=5.102)
                if len(saved) > 0 and "date" in saved[0]:
                    return "photo" + str(saved[0]["owner_id"]) + "_" + str(saved[0]["id"])
                else:
                    raise vk_upload_err("Can't upload photo")
            else:
                raise vk_upload_err("Can't upload photo")
        else:
            raise vk_upload_err("vk err")

    def _send_with_picture(self, messange, to):
        attachment_text = self._upload_photo()
        self.api.messages.send(message=messange, user_ids=to,
                                    random_id=random.randint(0, 2 ** 64), v="5.120",
                                    attachment=attachment_text)
        # except (vk_upload_err, cam_not_found):
        #     raise

    def _send_without_picture(self, messange, to):
        self.api.messages.send(message=messange, user_ids=to,
                               random_id=random.randint(0, 2 ** 64), v="5.120")

    def notify(self, messange):
        if self.settings["with_cam"]:
            try:
                self._send_with_picture(messange, self.settings["domain"])
            except (vk_upload_err, cam_not_found):
                if self.settings["no_cam_err"]:
                    self._send_without_picture(messange, self.settings["domain"])
                else:
                    raise
        else:
            self._send_without_picture(messange, self.settings["domain"])

        super().notify(messange)


if __name__ == '__main__':
    # s = input("Введите сообщение: ")
    from settings.settings import settings
    from WebCam.camdriver import VideoCamera
    settings = settings()
    a = vk_send(settings, VideoCamera(0, settings))
    a.notify("a")

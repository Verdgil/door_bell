import os
import subprocess
import threading
import time
import random

from notifications.base_notifi import base_notify


class audio(base_notify):
    def __init__(self, settings, not_used):
        self.setting = settings
        super().__init__(settings, not_used)

    def _th_play(self):
        f = open("/dev/null", "w")
        loop = " -loop 0 " if self.setting["loop"] else ""
        strs = "mplayer \"audio/" \
                + self.setting["audio"][random.randint(0, len(self.setting["audio"]) - 1)]
        strs += "\" -af volume=" + str(self.setting["volume"])
        strs += loop
        proc = subprocess.Popen(strs, shell=True, stdout=f, stderr=f)

    def notify(self, messange):
        th_player = threading.Thread(target=self._th_play)
        th_player.daemon = True
        th_player.start()
        time.sleep(self.setting["audio_time"])
        th_player._stop()
        os.system("killall -9 mplayer")
        super().notify(messange)


if __name__ == '__main__':
    from settings.settings import settings
    settings = settings()
    a = audio(settings)
    a.notify("a")
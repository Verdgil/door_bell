import json
import os


class settings:
    settings = None
    filename = None

    def __init__(self, filename="./settings.json"):
        self.read_settings(filename)

    def read_settings(self, filename):
        try:
            f = open(filename, "r")
        except FileNotFoundError:
            raise
        t = f.readlines()
        set_str = ""
        for i in t:
            set_str += i
        f.close()
        self.filename = filename
        self.settings = json.loads(set_str)
        self.settings["audio"] = os.listdir("audio")

    def get_raw_setting(self):
        return self.settings

    def write_settings(self):
        s = json.dumps(self.settings)
        f = open(self.filename, "w")
        print(s, file=f)
        f.close()

    def __getitem__(self, key):
        try:
            ret = self.settings[key]
        except KeyError:
            return None
        else:
            return ret

    def __setitem__(self, key, value):
        self.settings[key] = value
        self.write_settings()

    def keys(self):
        return self.settings.keys()

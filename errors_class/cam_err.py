class cam_not_found(Exception):
    def __init__(self, text=""):
        self.text = text

class cam_not_connected(Exception):
    def __init__(self, text=""):
        self.text = text
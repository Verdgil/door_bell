class vk_upload_err(Exception):
    def __init__(self, text=""):
        self.text = text
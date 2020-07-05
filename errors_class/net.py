class net_error(Exception):
    def __init__(self, text=""):
        self.text = text
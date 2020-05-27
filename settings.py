import json


def read_setting():
    try:
        f = open("settings.json", "r")
    except FileNotFoundError:
        raise
    t = f.readlines()
    set_str = ""
    for i in t:
        set_str += i
    ret = json.loads(set_str)
    f.close()
    return ret

def write_settings(set_lst):
    s = json.dumps(set_lst)
    f = open("settings.json", "w")
    print(s, file=f)
    f.close()
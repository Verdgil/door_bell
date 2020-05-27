import time

import yeelight
import settings

setting = settings.read_setting()


class lamp:
    lamp_bulb = None
    ip = 0

    def __init__(self):
        self.find_lamp_ip()
        self.lamp_bulb = yeelight.Bulb(self.ip, auto_on=True)
        self.proterius = None

    def find_lamp_ip(self):
        if "lamp_ip" in setting.keys():
            self.ip = setting["lamp_ip"]
        bulbs = yeelight.discover_bulbs()
        for b in bulbs:
            if "capabilities" in b.keys() and b["capabilities"]["name"].lower() == setting["lamp_name"]:
                self.ip = b["ip"]
        return self.ip

    def blink(self):
        self.read_proterius()
        for _ in range(setting["count"]):
            self.lamp_bulb.turn_on(effect="smooth", duration=0)
            self.lamp_bulb.set_brightness(setting["bright"])
            self.lamp_bulb.set_color_temp(setting["temperature"])
            time.sleep(setting["half_time"])
            self.lamp_bulb.turn_off()
            time.sleep(setting["half_time"])
        self.save_proterius()

    def read_proterius(self):
        self.proterius = self.lamp_bulb.get_properties()
        if self.proterius["power"] == "on":
            if self.proterius["flowing"] == "1":
                self.flow = self.lamp_bulb.get_properties(["flow_params"])


    def save_proterius(self):
        if self.proterius["power"] == "off":
            pass
        elif self.proterius["power"] == "on":
            if self.proterius["flowing"] == "0":
                if self.proterius["color_mode"] == "2": # Белый
                    self.lamp_bulb.set_color_temp(int(self.proterius["ct"]))
                    self.lamp_bulb.set_brightness(int(self.proterius["current_brightness"]))
                    self.lamp_bulb.set_power_mode(yeelight.PowerMode.NORMAL)
                    self.lamp_bulb.turn_on()
                elif self.proterius["color_mode"] == "1": # RGB
                    self.lamp_bulb.set_power_mode(yeelight.PowerMode.RGB)
                    self.lamp_bulb.turn_on()
                    self.lamp_bulb.set_rgb(*lamp.str_int_to_rgb(self.proterius["rgb"]))
                    self.lamp_bulb.set_brightness(int(self.proterius["current_brightness"]))
            else:
                self.lamp_bulb.turn_on()
                self.lamp_bulb.send_command("start_cf", [int(self.flow['flow_params'][0]),
                                                         int(self.flow['flow_params'][2]),
                                                         self.flow['flow_params'][4:]])


    @staticmethod
    def str_int_to_rgb(str_int):
        hex_color = hex(int(str_int))[2:]
        red = int(hex_color[0:2], 16)
        green = int(hex_color[2:4], 16)
        blue = int(hex_color[4:], 16)
        return [red, green, blue]


if __name__ == "__main__":
    lamp = lamp()
    lamp.blink()
    pass
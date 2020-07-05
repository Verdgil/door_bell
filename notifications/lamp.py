import time

import yeelight
from errors_class.net import net_error
import socket

from notifications.base_notifi import base_notify


class lamp(base_notify):
    lamp_bulb = None

    def __init__(self, settings, not_used):
        self.setting = settings
        self._find_lamp_ip()
        self._try_connect()
        self.lamp_bulb = yeelight.Bulb(self.setting["lamp_ip"], auto_on=True)
        self.proterius = None
        super().__init__(settings, not_used)

    def _try_connect(self):
        sock = socket.socket()
        exc = False
        try:
            sock.connect((self.setting["lamp_ip"], 55443))
        except socket.error:
            exc = True
        finally:
            sock.close()
        if exc:
            raise net_error("No connect to lamp")

    def _find_lamp_ip(self):
        bulbs = yeelight.discover_bulbs()
        if "lamp_ip" not in self.setting.keys() and len(bulbs) > 0:
            for b in bulbs:
                if "capabilities" in b.keys() and b["capabilities"]["name"].lower() == self.setting["lamp_name"]:
                    self.setting["lamp_ip"] = b["ip"]
        else:
            pass

    def _blink(self):
        self._read_proterius()
        for _ in range(self.setting["count"]):
            self.lamp_bulb.turn_on(effect="smooth", duration=0)
            self.lamp_bulb.set_brightness(self.setting["bright"])
            self.lamp_bulb.set_color_temp(self.setting["temperature"])
            time.sleep(self.setting["half_time"])
            self.lamp_bulb.turn_off()
            time.sleep(self.setting["half_time"])
        self._save_proterius()

    def _read_proterius(self):
        self.proterius = self.lamp_bulb.get_properties()
        if self.proterius["power"] == "on":
            if self.proterius["flowing"] == "1":
                self.flow = self.lamp_bulb.get_properties(["flow_params"])

    def _save_proterius(self):
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
                    self.lamp_bulb.set_rgb(*lamp._str_int_to_rgb(self.proterius["rgb"]))
                    self.lamp_bulb.set_brightness(int(self.proterius["current_brightness"]))
            else:
                self.lamp_bulb.turn_on()
                self.lamp_bulb.send_command("start_cf", [int(self.flow['flow_params'][0]),
                                                         int(self.flow['flow_params'][2]),
                                                         self.flow['flow_params'][4:]])

    @staticmethod
    def _str_int_to_rgb(str_int):
        hex_color = hex(int(str_int))[2:]
        red = int(hex_color[0:2], 16)
        green = int(hex_color[2:4], 16)
        blue = int(hex_color[4:], 16)
        return [red, green, blue]

    def notify(self, messange):
        self._try_connect()
        self._blink()
        super().notify(messange)


if __name__ == "__main__":
    from settings.settings import settings
    settings = settings()
    lamp = lamp(settings)
    lamp.notify("")
    pass
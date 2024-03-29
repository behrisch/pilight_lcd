#!/usr/bin/env python
from __future__ import print_function
import os
import time
import datetime
import json
from pilight import pilight
from hd44780 import HD44780


class PilightConnector:
    def __init__(self, values, lcd_config):
        cfg = json.load(open(lcd_config)) if lcd_config else {}
        self._lcd = HD44780(**cfg.get("hd44780", {}))
        self._line_mapping = {}
        mapping = cfg.get("line_mapping", {1:0, 2:1, 3:2, 5:3, 4:4, 6:5})
        for key, value in mapping.items():
            self._line_mapping[int(key)] = int(value)
        self._outdated = datetime.timedelta(**cfg.get("outdated", {"hours": 1}))
        self._debug = cfg.get("debug", False)
        self._values = values
        for v in values.values():
            self.update(v)

    def update(self, v):
        msg = "%(name)s %(temperature)02.1f%(unit)s %(humidity).0f%%" % v
        if self._debug:
            print(msg)
        if v["id"] in self._line_mapping:
            self._lcd.message(msg, self._line_mapping[v["id"]])

    def handle_code(self, code):
        if self._debug:
            print("received", code)
        if "message" in code and code["message"].get("id") in self._values:
            msg = code["message"]
            if "temperature" in msg:
                v = self._values[msg["id"]]
                v.update(msg)
                now = datetime.datetime.now()
                if self._debug:
                    if "last_update" in v:
                        print(now, "update for", v["name"], "after", now - v["last_update"])
                    else:
                        print(now, "first update for", v["name"])
                v["last_update"] = now
                self.update(v)
        self.check_outdated()

    def check_outdated(self):
        now = datetime.datetime.now()
        for v in self._values.values():
            delta = datetime.timedelta(days=100)
            if "last_update" in v:
                delta = now - v["last_update"]
            unit = v["unit"].lower() if delta > self._outdated else v["unit"].upper()
            if unit != v["unit"]:
                v["unit"] = unit
                self.update(v)


if __name__ == '__main__':
    config = json.load(open("/etc/pilight/config.json"))
    values = {}
    for key, value in config["devices"].items():
        if "id" in value and "id" in value["id"][0]:
            value["id"] = value["id"][0]["id"]
            if key in config["gui"]:
                name = config["gui"][key]["name"].replace(" und ", "&")
            else:
                name = key
            value["name"] = (name + 10 * " ")[:10]
            value["unit"] = "c"
            values[value["id"]] = value
    lcd_config = None
    for path in ("/etc/pilight", os.path.dirname("__file__")):
        if os.path.exists(os.path.join(path, "lcd-config.json")):
            lcd_config = os.path.join(path, "lcd-config.json")

    while True:
        connector = PilightConnector(values, lcd_config)
        print(values)

        # Create new pilight connection that runs on localhost with port 5000
        pilight_client = pilight.Client(host='127.0.0.1', port=config.get("settings", {}).get("port", 5000))

        # Set a data handle that is called on received data
        pilight_client.set_callback(connector.handle_code)
        pilight_client.start()  # Start the receiver

        # restart every hour becuase sometimes the lcd connection breaks
        time.sleep(3600)
        pilight_client.stop()  # Stop the receiver

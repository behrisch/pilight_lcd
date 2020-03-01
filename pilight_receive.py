#!/usr/bin/env python
import time
import json
from pilight import pilight
from hd44780 import HD44780

LCD = HD44780()
VALUES = {}
LINE_MAPPING = {1:0, 2:1, 3:2, 5:3}


def update(v):
    msg = "%s: %sC %s%%" % (v["name"], v["temperature"], v["humidity"])
    print(msg)
    if value["id"] in LINE_MAPPING:
        LCD.message(msg, LINE_MAPPING[value["id"]])


def handle_code(code):  # Simply  print received data from pilight
    """Handle to just prints the received code."""
    if "message" in code and "id" in code["message"]:
        VALUES[code["message"]["id"]].update(code["message"])
        update(VALUES[code["message"]["id"]])


# pylint: disable=C0103
if __name__ == '__main__':
    config = json.load(open("/etc/pilight/config.json"))
    id_key = {}
    for key, value in config["devices"].items():
        if "id" in value and "id" in value["id"][0]:
            value["id"] = value["id"][0]["id"]
            if key in config["gui"]:
                value["name"] = config["gui"][key]["name"]
            VALUES[value["id"]] = value
            update(value)
    print(VALUES)
    # Create new pilight connection that runs on localhost with port 5000
    pilight_client = pilight.Client(host='127.0.0.1', port=5000)

    # Set a data handle that is called on received data
    pilight_client.set_callback(handle_code)
    pilight_client.start()  # Start the receiver

    # You have 10 seconds to print all the data the pilight-daemon receives
    time.sleep(15000)
    pilight_client.stop()  # Stop the receiver

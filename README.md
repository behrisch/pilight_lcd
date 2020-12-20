# pilight_lcd
Connecting LCDs as display for a pilight server

## Installation (tested only on Raspberry Pi 3 with Debian based Linux)
- Install pilight: https://manual.pilight.org/installation.html
- Install pilight python module
```
sudo apt install git python-pip python-setuptools python-wheel python-rpi.gpio
sudo pip install pilight
```
- Clone repo
- `git clone https://www.github.com/behrisch/pilight_lcd`
- Adapt your wiring and the dimensions of your LCD in the constructor of HD44780 (file hd44780.py, line 19-20)
- Start the script using `sudo pilight_lcd/pilight_receive.py`

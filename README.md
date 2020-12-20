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
- Adapt your wiring and the dimensions of your LCD in the lcd-config.json
- Start the script using `sudo pilight_lcd/pilight_receive.py`

### Optional steps to run it as a service
- Copy the script and the config to a location of your choice (the config needs to be in the same directory as the script or in /etc/pilight)
- Adapt the service file with the location of the script
- Copy it to /etc/systemd/system
- Start it using `sudo systemctl start pilight_lcd`
- Test whether it was successful: `sudo systemctl status pilight_lcd`
- If you want to start it on every boot: `sudo systemctl enable pilight_lcd`

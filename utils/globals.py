
import os
from configparser import ConfigParser


WIDTH = 250
HEIGHT = 300

FPS = 15

CONFIG_DEFAULT_VALUES = {
    "work": "1500",
    "shortBreak": "300",
    "longBreak": "1800",
    "interval": "4",
    "isAutoSwitchOn": "0",
    "isSoundOn": "0"
}

COLOR_PRIMARY = (56, 42, 29)   #382a1d | mocha
COLOR_SECONDARY = (182, 155, 125)   #b69b7d | heavy cream
COLOR_BACKGROUND = (222, 203, 177)   #decbb1 | whip

COLOR_MACOS_RED = (255, 96, 92)   #ff605c | sunset orange
COLOR_MACOS_YELLOW = (255, 189, 68)   #ffbd44 | pastel orange
COLOR_MACOS_GREEN = (0, 202, 78)   #00ca4e | malachite

BASE_DIR = os.path.join("Python", "Project Pomodoro")

CONFIG_PATH = os.path.join(BASE_DIR, "configs", "config.ini")
FONT_PATH = os.path.join(BASE_DIR, "fonts", "JetBrainsMonoNL-Bold.ttf")
GLOBALS_PATH = os.path.join(BASE_DIR, "utils", "globals.py")
CONTROL_PATH = os.path.join(BASE_DIR, "utils", "control.py")
UTILS_PATH = os.path.join(BASE_DIR, "utils", "utils.py")

ABOUT_ADDRESS = "https://www.buymeacoffee.com/ntduck"

configFileValueTimeLengths = [0, 0, 0]
configFileValueInterval = 0
configFileValueIsAutoSwitchOn = 0
configFileValueIsSoundOn = 0


CONFIGPARSER = ConfigParser()
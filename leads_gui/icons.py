from os.path import abspath as _abspath

from PIL import Image as _Image
from customtkinter import CTkImage as _CTkImage

_ASSETS_PATH = _abspath(__file__)[:-8] + "assets"
_ICONS_PATH = _ASSETS_PATH + "/icons"

WheelSpeed = _CTkImage(_Image.open(_ICONS_PATH + "/wheel_speed.webp"), size=(40, 40))

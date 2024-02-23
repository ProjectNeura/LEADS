from os.path import abspath as _abspath

from PIL import Image as _Image
from customtkinter import CTkImage as _CTkImage

from leads import set_on_register_config as _set_on_register_config, OnRegisterConfig as _OnRegisterConfig, \
    get_config as _get_config
from leads_gui.config import Config

_ASSETS_PATH = _abspath(__file__)[:-8] + "assets"
_ICONS_PATH = _ASSETS_PATH + "/icons"

Battery = _CTkImage(_Image.open(_ICONS_PATH + "/battery.png"))
Engine = _CTkImage(_Image.open(_ICONS_PATH + "/engine.png"))
HighBeam = _CTkImage(_Image.open(_ICONS_PATH + "/high-beam.png"))
Light = _CTkImage(_Image.open(_ICONS_PATH + "/light.png"))
Speed = _CTkImage(_Image.open(_ICONS_PATH + "/speed.png"))


def _on_register_config(chain: _OnRegisterConfig[Config] | None) -> _OnRegisterConfig[Config]:
    def _(config: Config) -> None:
        if chain:
            chain(config)
        Battery.configure(size=(config.font_size_medium, config.font_size_medium))
        Engine.configure(size=(config.font_size_medium, config.font_size_medium))
        HighBeam.configure(size=(config.font_size_medium, config.font_size_medium))
        Light.configure(size=(config.font_size_medium, config.font_size_medium))
        Speed.configure(size=(config.font_size_medium, config.font_size_medium))

    return _


_set_on_register_config(_on_register_config)
if _config := _get_config(Config):
    _on_register_config(None)(_config)

from importlib.util import spec_from_file_location as _spec_from_file_location, module_from_spec as _module_from_spec
from os.path import abspath as _abspath
from os.path import exists as _exists
from typing import Literal as _Literal

from customtkinter import set_default_color_theme as _set_default_color_theme

from leads import register_controller as _register_controller, MAIN_CONTROLLER as _MAIN_CONTROLLER, \
    L as _L, load_config as _load_config, register_config as _register_config, release as _release
from leads_gui import Config as _Config


def run(config: str,
        devices: str,
        main: str,
        register: _Literal["systemd", "config", "reverse_proxy"],
        theme: str,
        magnify_font_sizes: float,
        emu: bool,
        auto_mfs: bool,
        ignore_import_error: bool) -> int:
    if register == "systemd":
        from ._bootloader import register_leads_vec as _create_service

        _create_service()
        _L.debug("Service registered")
        _L.debug(f"Service script is located at \"{_abspath(__file__)[:-6]}_bootloader/leads-vec.service.sh\"")
    elif register == "config":
        if _exists("config.json"):
            r = input("\"config.json\" already exists. Overwrite? (Y/n) >>>").lower()
            if r.lower() != "y":
                _L.error("Aborted")
                return 1
        with open("config.json", "w") as f:
            f.write(str(_Config({})))
        _L.debug("Configuration file saved to \"config.json\"")
    elif register == "reverse_proxy":
        from ._bootloader import start_frpc as _start_frpc

        _start_frpc()
        _L.debug("`frpc` started")
    config = _load_config(config, _Config) if config else _Config({})
    _L.debug("Configuration loaded:", str(config))
    if t := theme:
        _set_default_color_theme(t)
    if (f := magnify_font_sizes) != 1:
        config.magnify_font_sizes(f)
    if auto_mfs:
        config.auto_magnify_font_sizes()
    _register_config(config)
    spec = _spec_from_file_location("main", main)
    spec.loader.exec_module(main := _module_from_spec(spec))
    try:
        main = getattr(main, "main")
    except AttributeError:
        raise ImportError(f"No main function in \"{main}\"")

    try:
        if emu:
            raise SystemError("User specifies to use emulator")
        spec = _spec_from_file_location("_", devices)
        spec.loader.exec_module(_module_from_spec(spec))
    except (ImportError, SystemError) as e:
        _L.debug(repr(e))
        if isinstance(e, ImportError):
            if ignore_import_error:
                _L.debug(f"Ignoring import error: {repr(e)}")
                return main()
            else:
                _L.warn(f"Specified devices module ({devices}) is not available, using emulation module instead...")
        _release()
        try:
            from leads_emulation import SinController as _Controller

            _register_controller(_MAIN_CONTROLLER, _Controller(0, 200, .05))
        except ImportError as e:
            _L.error(f"Emulator error: {repr(e)}")
            return 1
    return main()

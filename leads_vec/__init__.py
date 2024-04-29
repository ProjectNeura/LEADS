from importlib.util import find_spec as _find_spec

if not _find_spec("pynput"):
    raise ImportError("Please install `pynput` to run this module\n>>>pip install pynput")

a = "customtkinter gpiozero lgpio Pillow pynput pyserial pynmea2 PySDL2".split()
a.sort()
print(" ".join(a))

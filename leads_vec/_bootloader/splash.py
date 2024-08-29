from os.path import abspath as _abspath
from shutil import copyfile as _copyfile, move as _move

from leads_gui.system import get_system_kernel as _get_system_kernel


def register_splash_screen() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    _move("/usr/share/plymouth/themes/spinner/bgrt-fallback.png",
          "/usr/share/plymouth/themes/spinner/bgrt-fallback-backup.png")
    _copyfile(f"{_abspath(__file__)[:-9]}bgrt-fallback.png", "/usr/share/plymouth/themes/spinner/bgrt-fallback.png")
    _move("/usr/share/plymouth/themes/spinner/watermark.png", "/usr/share/plymouth/themes/spinner/watermark-backup.png")
    _copyfile(f"{_abspath(__file__)[:-9]}watermark.png", "/usr/share/plymouth/themes/spinner/watermark.png")


def register_lock_screen() -> None:
    if _get_system_kernel() != "linux":
        raise SystemError("Unsupported operating system")
    _move("/usr/share/plymouth/ubuntu-logo.png", "/usr/share/plymouth/ubuntu-logo-backup.png")
    _copyfile(f"{_abspath(__file__)[:-9]}watermark.png", "/usr/share/plymouth/ubuntu-logo.png")

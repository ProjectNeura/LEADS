from typing import Any as _Any

from leads import ConfigTemplate as _ConfigTemplate


class Config(_ConfigTemplate):
    def __init__(self, base: dict[str, _Any]) -> None:
        super().__init__(base)
        self.width: int = 720
        self.height: int = 480
        self.fullscreen: bool = False
        self.no_title_bar: bool = False
        self.manual_mode: bool = False
        self.refresh_rate: int = 30
        self.font_size_small: int = 12
        self.font_size_medium: int = 24
        self.font_size_large: int = 40
        self.font_size_x_large: int = 56
        self.comm_addr: str = "127.0.0.1"
        self.comm_port: int = 16900
        self.data_dir: str = "./data"
        self.enable_data_persistence: bool = True
        self.refresh()

from typing import Any as _Any, Literal as _Literal

from leads import ConfigTemplate as _ConfigTemplate


class Config(_ConfigTemplate):
    def __init__(self, base: dict[str, _Any]) -> None:
        self.width: int = 720
        self.height: int = 480
        self.fullscreen: bool = False
        self.no_title_bar: bool = False
        self.theme_mode: _Literal["system", "light", "dark"] = "system"
        self.manual_mode: bool = False
        self.refresh_rate: int = 30
        self.m_ratio: float = .7
        self.font_size_small: int = 14
        self.font_size_medium: int = 28
        self.font_size_large: int = 42
        self.font_size_x_large: int = 56
        self.comm_addr: str = "127.0.0.1"
        self.comm_port: int = 16900
        self.save_data: bool = False
        super().__init__(base)

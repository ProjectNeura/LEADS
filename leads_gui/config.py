from typing import Any as _Any, Literal as _Literal

from leads import ConfigTemplate as _ConfigTemplate, L as _L, get_config as _get_config


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

    def magnify_font_sizes(self, factor: float) -> None:
        """
        Magnify font sizes by the factor.
        :param factor: the factor
        """
        if _get_config():
            raise RuntimeError("This method must be called before the config is registered")
        self._frozen = False
        self.font_size_small = int(self.font_size_small * factor)
        self.font_size_medium = int(self.font_size_medium * factor)
        self.font_size_large = int(self.font_size_large * factor)
        self.font_size_x_large = int(self.font_size_x_large * factor)
        self._frozen = True
        _L.debug(f"Font sizes magnified by {factor}")

    def auto_magnify_font_sizes(self) -> None:
        """
        Automatically magnify font sizes to match the original proportion.
        """
        self.magnify_font_sizes(self.width / Config({}).width)

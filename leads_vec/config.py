from typing import Any as _Any

from leads_gui import Config as _Config


class Config(_Config):
    def __init__(self, base: dict[str, _Any]) -> None:
        self.comm_port: int = 16900
        self.comm_stream: bool = False
        self.comm_stream_port: int = 16901
        self.data_dir: str = "data"
        self.use_ltm: bool = False
        super().__init__(base)

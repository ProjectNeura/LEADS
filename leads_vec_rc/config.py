from typing import Any as _Any

from leads import ConfigTemplate as _ConfigTemplate


class Config(_ConfigTemplate):
    def __init__(self, base: dict[str, _Any]) -> None:
        self.comm_addr: str = "127.0.0.1"
        self.comm_port: int = 16900
        self.data_dir: str = "data"
        self.save_data: bool = False
        super().__init__(base)

from typing import override

from leads import device, MAIN_CONTROLLER, L
from leads_video import Camera

import_error: ImportError | None = None
try:
    from leads_vec.devices import _
except ImportError as e:
    import_error = e


# @device(("front_vc", "left_vc", "right_vc", 'rear_vc'), MAIN_CONTROLLER, [(0,), (1,), (2,), (3,)])
@device("front_vc", MAIN_CONTROLLER, (0,))
class Cameras(Camera):
    @override
    def initialize(self, *parent_tags: str) -> None:
        super().initialize(*parent_tags)
        L.info("Camera initializing")


if import_error:
    raise import_error

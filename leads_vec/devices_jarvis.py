from typing import override

from leads import device, MAIN_CONTROLLER, mark_device, FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, \
    REAR_VIEW_CAMERA
from leads_video import Camera, base64_encode

import_error: ImportError | None = None
try:
    from leads_vec.devices import _
except ImportError as e:
    import_error = e


@device((FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA), MAIN_CONTROLLER, [
    (0, (480, 360)), (1, (480, 360)), (2, (480, 360)), (3, (480, 360))
])
class Cameras(Camera):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "Jarvis")
        super().initialize(*parent_tags)

    @override
    def read(self) -> str:
        return base64_encode(super().read(), "RGB")


if import_error:
    raise import_error

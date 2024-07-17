from typing import override

from leads import device, MAIN_CONTROLLER, mark_device, FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, \
    REAR_VIEW_CAMERA, require_config
from leads_gui import Config
from leads_video import LowLatencyBase64Camera

import_error: ImportError | None = None
try:
    from leads_vec.devices import _
except ImportError as e:
    import_error = e

config: Config = require_config()
CAMERA_RESOLUTION: tuple[int, int] | None = config.get("camera_resolution")
CAMERA_TAGS: list[str] = []
CAMERA_ARGS: list[tuple[int, tuple[int, int] | None]] = []
if (port := config.get("front_view_camera_port")) is not None:
    CAMERA_TAGS.append(FRONT_VIEW_CAMERA)
    CAMERA_ARGS.append((port, CAMERA_RESOLUTION))
if (port := config.get("left_view_camera_port")) is not None:
    CAMERA_TAGS.append(LEFT_VIEW_CAMERA)
    CAMERA_ARGS.append((port, CAMERA_RESOLUTION))
if (port := config.get("right_view_camera_port")) is not None:
    CAMERA_TAGS.append(RIGHT_VIEW_CAMERA)
    CAMERA_ARGS.append((port, CAMERA_RESOLUTION))
if (port := config.get("rear_view_camera_port")) is not None:
    CAMERA_TAGS.append(REAR_VIEW_CAMERA)
    CAMERA_ARGS.append((port, CAMERA_RESOLUTION))


@device(CAMERA_TAGS, MAIN_CONTROLLER, CAMERA_ARGS)
class Cameras(LowLatencyBase64Camera):
    @override
    def initialize(self, *parent_tags: str) -> None:
        mark_device(self, "Jarvis")
        super().initialize(*parent_tags)


if import_error:
    raise import_error

from leads import has_device as _has_device, get_device as _get_device
from leads_video.camera import Camera


def get_camera(tag: str, required_type: type[Camera] = Camera) -> Camera | None:
    if not _has_device(tag):
        return None
    cam = _get_device(tag)
    if not isinstance(cam, required_type):
        raise TypeError(f"Device \"{tag}\" is supposed to be a camera")
    return cam

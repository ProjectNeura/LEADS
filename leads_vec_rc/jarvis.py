from typing import Any as _Any

from leads_jarvis import Detection, PretrainedYOLO

from leads_video import base64_decode, base64_encode

_model: Detection = PretrainedYOLO("yolov8n")


def process(d: dict[str, _Any]) -> dict[str, _Any]:
    for key in "front_view_base64", "left_view_base64", "right_view_base64", "rear_view_base64":
        if key in d.keys():
            img = base64_decode(d[key])
            d[key] = "" if img is None else base64_encode(_model.mark(img, filter_type=("car",)))
    return d

from base64 import b64encode
from io import BytesIO
from time import time
from typing import Callable

from PIL.Image import open
from customtkinter import CTkLabel, DoubleVar
from cv2 import VideoCapture, imencode, IMWRITE_JPEG_QUALITY, CAP_PROP_FPS

from leads import L, require_config
from leads_gui import RuntimeData, Pot, ContextManager, Speedometer


def video_tester(container: Callable[[], None]) -> float:
    start = time()
    sum_delay = 0
    i = 0
    while True:
        if (t := time()) - start > 10:
            return sum_delay / i
        container()
        sum_delay += time() - t
        i += 1


def video_test() -> dict[str, float]:
    r = {}
    vc = VideoCapture(require_config().get("benchmark_camera_port", 0))
    r["camera fps"] = vc.get(CAP_PROP_FPS)
    if not vc.isOpened():
        L.error("No camera available")
        return r

    def test1() -> None:
        vc.read()

    def test2() -> None:
        _, frame = vc.read()
        imencode(".jpg", frame, (IMWRITE_JPEG_QUALITY, 90))[1].tobytes()

    def test3() -> None:
        _, frame = vc.read()
        im = imencode(".jpg", frame, (IMWRITE_JPEG_QUALITY, 90))[1].tobytes()
        b64encode(im)

    def test4() -> None:
        _, frame = vc.read()
        im = imencode(".jpg", frame, (IMWRITE_JPEG_QUALITY, 90))[1].tobytes()
        b64encode(im)
        open(BytesIO(im))

    r["video capture"] = 1 / video_tester(test1)
    r["video capture + encoding"] = 1 / video_tester(test2)
    r["video capture + Base64 encoding"] = 1 / video_tester(test3)
    r["video capture + PIL"] = 1 / video_tester(test4)
    return r


class Callbacks(object):
    def __init__(self) -> None:
        self.t: float = time()
        self.speed: DoubleVar | None = None

    def on_refresh(self, window: Pot) -> None:
        self.speed.set((d := time() - self.t) * 20)
        if d > 10:
            window.kill()


def main() -> int:
    report = {}
    L.info("GUI test starting, this takes about 10 seconds")
    rd = RuntimeData()
    callbacks = Callbacks()
    w = Pot(800, 256, 30, rd, callbacks.on_refresh, "Benchmark", no_title_bar=False)
    callbacks.speed = DoubleVar(w.root())
    uim = ContextManager(w)
    uim.layout([[CTkLabel(w.root(), text="Do NOT close the window", height=240),
                 Speedometer(w.root(), height=240, variable=callbacks.speed)]])
    uim.show()
    L.info("GUI test complete")
    L.info("Video test starting, this takes about 40 seconds")
    report["gui"] = w.frame_rate()
    report.update(video_test())
    L.info("Video test complete")
    for k, v in report.items():
        L.info(f"{k}: {v:.3f}")
    camera_fps = report.pop("camera fps")
    baseline = {"gui": 30, "video capture": camera_fps, "video capture + encoding": camera_fps,
                "video capture + Base64 encoding": camera_fps, "video capture + PIL": camera_fps}
    score = 0
    for k, v in report.items():
        score += v / baseline[k]
    L.info(f"Score: {100 * score / len(report):.2f}%")
    return 0


_: None = None

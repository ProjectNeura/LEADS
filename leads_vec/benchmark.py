from base64 import b64encode
from io import BytesIO
from time import time
from typing import Callable

from PIL.Image import open
from customtkinter import CTkLabel, DoubleVar
from cv2 import VideoCapture, imencode, IMWRITE_JPEG_QUALITY

from leads import L
from leads_gui import RuntimeData, Window, ContextManager, Speedometer


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
    vc = VideoCapture(1)
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
        open(BytesIO(im))

    r["video capture"] = video_tester(test1) * 1000
    r["video capture and encoding"] = video_tester(test2) * 1000
    r["video capture and Base64 encoding"] = video_tester(test3) * 1000
    r["video capture and PIL"] = video_tester(test4) * 1000
    return r


class Callbacks(object):
    def __init__(self) -> None:
        self.t: float = time()
        self.speed: DoubleVar | None = None

    def on_refresh(self, window: Window) -> None:
        self.speed.set((d := time() - self.t) * 20)
        if d > 10:
            window.kill()


def main() -> int:
    report = {}
    L.info("GUI test starting, this takes about 10 seconds")
    rd = RuntimeData()
    callbacks = Callbacks()
    w = Window(800, 256, 30, rd, callbacks.on_refresh, "Benchmark", no_title_bar=False)
    callbacks.speed = DoubleVar(w.root())
    uim = ContextManager(w)
    uim.layout([[CTkLabel(w.root(), text="Benchmark Ongoing", height=240),
                 Speedometer(w.root(), height=240, variable=callbacks.speed)]])
    uim.show()
    L.info("GUI test complete")
    L.info("Video test starting, this takes about 40 seconds")
    report["frame rate"] = w.frame_rate()
    report["net delay"] = w.net_delay() * 1000
    report.update(video_test())
    L.info("Video test complete")
    for k, v in report.items():
        L.info(f"{k}: {v:.3f}")
    return 0


_: None = None

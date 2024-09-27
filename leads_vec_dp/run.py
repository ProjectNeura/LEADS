from atexit import register as _register
from typing import Any as _Any

from yaml import load as _load, SafeLoader as _SafeLoader

from leads import L as _L
from leads.data_persistence import CSVDataset as _CSVDataset
from leads.data_persistence.analyzer import InferredDataset as _InferredDataset, Inference as _Inference, \
    SafeSpeedInference as _SafeSpeedInference, SpeedInferenceByAcceleration as _SpeedInferenceByAcceleration, \
    SpeedInferenceByMileage as _SpeedInferenceByMileage, \
    SpeedInferenceByGPSGroundSpeed as _SpeedInferenceByGPSGroundSpeed, \
    SpeedInferenceByGPSPosition as _SpeedInferenceByGPSPosition, \
    ForwardAccelerationInferenceBySpeed as _ForwardAccelerationInferenceBySpeed, \
    MileageInferenceBySpeed as _MileageInferenceBySpeed, \
    MileageInferenceByGPSPosition as _MileageInferenceByGPSPosition, \
    VisualDataRealignmentByLatency as _VisualDataRealignmentByLatency
from leads.data_persistence.analyzer.processor import Processor as _Processor
from leads_video import extract_video as _extract_video

INFERENCE_METHODS: dict[str, type[_Inference]] = {
    "safe-speed": _SafeSpeedInference,
    "speed-by-acceleration": _SpeedInferenceByAcceleration,
    "speed-by-mileage": _SpeedInferenceByMileage,
    "speed-by-gps-ground-speed": _SpeedInferenceByGPSGroundSpeed,
    "speed-by-gps-position": _SpeedInferenceByGPSPosition,
    "forward-acceleration-by-speed": _ForwardAccelerationInferenceBySpeed,
    "mileage-by-speed": _MileageInferenceBySpeed,
    "mileage-by-gps-position": _MileageInferenceByGPSPosition,
    "visual-data-realignment-by-latency": _VisualDataRealignmentByLatency
}


def _optional_kwargs(source: dict[str, _Any], key: str) -> dict[str, _Any]:
    return source[key] if key in source else {}


def run(target: str) -> int:
    with open(target) as f:
        target = _load(f.read(), _SafeLoader)
    if "inferences" in target:
        dataset = _InferredDataset(target["dataset"])
        inferences = target["inferences"]
        methods = []
        for method in inferences["methods"]:
            methods.append(INFERENCE_METHODS[method]())
        inferences.pop("methods")
        repeat = 1
        if "repeat" in inferences:
            repeat = inferences["repeat"]
            inferences.pop("repeat")
        for _ in range(repeat):
            _L.info(f"Affected {(n := dataset.complete(*methods, **inferences))} row{"s" if n > 1 else ""}")
    else:
        dataset = _CSVDataset(target["dataset"])
    _register(dataset.close)
    processor = _Processor(dataset)
    for job in target["jobs"]:
        _L.info(f"Executing job {job["name"]}...")
        match job["uses"]:
            case "bake":
                processor.bake()
                _L.info("Baking Results", *processor.baking_results(), sep="\n")
            case "process":
                processor.process(**_optional_kwargs(job, "with"))
                _L.info("Results", *processor.results(), sep="\n")
            case "draw-lap":
                processor.draw_lap(**_optional_kwargs(job, "with"))
            case "suggest-on-lap":
                _L.info(*processor.suggest_on_lap(job["with"]["lap_index"]), sep="\n")
            case "draw-comparison-of-laps":
                processor.draw_comparison_of_laps(**_optional_kwargs(job, "with"))
            case "extract-video":
                _extract_video(dataset, file := job["with"]["file"], job["with"]["tag"])
                _L.info(f"Video saved as {file}")
            case "save-as":
                dataset.save(file := job["with"]["file"])
                _L.info(f"Dataset saved as {file}")

    return 0

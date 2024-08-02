from atexit import register as _register

from yaml import load as _load, SafeLoader as _SafeLoader

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

INFERENCES: dict[str, type[_Inference]] = {
    "safe-speed": _SafeSpeedInference,
    "speed-by-acceleration": _SpeedInferenceByAcceleration,
    "speed-by-mileage": _SpeedInferenceByMileage,
    "speed-by-gps-ground-speed": _SpeedInferenceByGPSGroundSpeed,
    "speed-by-gps-position": _SpeedInferenceByGPSPosition,
    "forward-acceleration-by-speed": _ForwardAccelerationInferenceBySpeed,
    "milage-by-speed": _MileageInferenceBySpeed,
    "milage-by-gps-position": _MileageInferenceByGPSPosition,
    "visual-data-realignment-by-latency": _VisualDataRealignmentByLatency
}


def run(target: str) -> int:
    with open(target) as f:
        target = _load(f.read(), _SafeLoader)
    if "inferences" in target.keys():
        dataset = _InferredDataset(target["dataset"])
        inferences = []
        kwargs = {}
        for inference in target["inferences"]:
            if isinstance(inference, dict):
                kwargs.update(inference)
            else:
                inferences.append(INFERENCES[inference]())
        dataset.complete(*inferences, **kwargs)
    else:
        dataset = _CSVDataset(target["dataset"])
    _register(dataset.close)
    return 0

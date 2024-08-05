from leads import controller, MAIN_CONTROLLER, require_config, VisualDataContainer, DataContainer, device, \
    FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA
from leads.data_persistence import CSVDataset, VISUAL_HEADER_ONLY
from leads_emulation.replay import ReplayController, ReplayCamera
from leads_vec.config import Config

config: Config = require_config()
CAMERA_RESOLUTION: tuple[int, int] | None = config.get("camera_resolution")
dataset: CSVDataset = CSVDataset(f"{config.data_dir}/main.csv")
visual: bool = set(VISUAL_HEADER_ONLY).issubset(dataset.read_header())


@controller(MAIN_CONTROLLER, args=(dataset, VisualDataContainer if visual else DataContainer))
class MainController(ReplayController[DataContainer]):
    pass


if visual:
    @device((FRONT_VIEW_CAMERA, LEFT_VIEW_CAMERA, RIGHT_VIEW_CAMERA, REAR_VIEW_CAMERA), MAIN_CONTROLLER, [
        ("front", CAMERA_RESOLUTION), ("left", CAMERA_RESOLUTION), ("right", CAMERA_RESOLUTION),
        ("rear", CAMERA_RESOLUTION)
    ])
    class Cameras(ReplayCamera):
        pass

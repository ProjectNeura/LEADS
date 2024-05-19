from leads import controller, MAIN_CONTROLLER, require_config, DataContainer
from leads.data_persistence import CSVDataset
from leads_emulation.replay import ReplayController


@controller(MAIN_CONTROLLER, args=(CSVDataset(f"{require_config().data_dir}/main.csv"), DataContainer))
class MainController(ReplayController[DataContainer]):
    pass

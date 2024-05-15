from leads import controller, MAIN_CONTROLLER, require_config
from leads.data_persistence import CSVDataset
from leads_emulation.replay import ReplayController


@controller(MAIN_CONTROLLER, args=(CSVDataset(f"{require_config().data_dir}/main.csv"),))
class MainController(ReplayController):
    pass

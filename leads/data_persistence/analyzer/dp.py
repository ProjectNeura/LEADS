from leads.data_persistence.analyzer.processor import Processor
from leads.data_persistence.core import CSVDataset


class DynamicProcessor(Processor):
    def __init__(self, dataset: CSVDataset) -> None:
        super().__init__(dataset)

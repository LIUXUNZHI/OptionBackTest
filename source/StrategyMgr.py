from source import DataMgr

class StrategyMgr(object):
    def __init__(self,start_date, end_date):
        self._data_driver = DataMgr(start_date, end_date)
        self._data =
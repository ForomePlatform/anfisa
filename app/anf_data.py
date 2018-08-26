import logging
from StringIO import StringIO

from .view_setup import ViewSetup
from view.dataset import DataSet
from view.checker import ViewDataChecker
from .search_setup import MainLegend
from search.hot_index import HotIndex
from .view_cfg import setupRecommended
#===============================================
class AnfisaData:
    sSets = dict()
    sFilters = dict()
    sDefaultSetName = None

    @classmethod
    def setup(cls, config):
        setupRecommended()
        for descr in config["datasets"]:
            set_name = descr["name"]
            if cls.sDefaultSetName is None:
                cls.sDefaultSetName = set_name
            if descr["kind"] == "a-json":
                cls.sSets[set_name] = DataSet(
                    ViewSetup, set_name, descr["file"])
            else:
                assert False
        for data_set in cls.sSets.values():
            ViewDataChecker.check(ViewSetup, data_set)
            MainLegend.testDataSet(data_set)
        rep_out = StringIO()
        MainLegend.setup(rep_out)
        if not MainLegend.isOK():
            logging.fatal("FILTER LEGEND FAILED\n" + rep_out.gevalue())
        for name, data_set in cls.sSets.items():
            cls.sFilters[name] = HotIndex(data_set, MainLegend)
        logging.warning(MainLegend.getStatusInfo())

    @classmethod
    def getSet(cls, set_name = None):
        if set_name is None:
            set_name = cls.sDefaultSetName
        return cls.sSets.get(set_name)

    @classmethod
    def getIndex(cls, set_name = None):
        if set_name is None:
            set_name = cls.sDefaultSetName
        return cls.sFilters.get(set_name)

    @classmethod
    def getSetNames(cls):
        return cls.sSets.keys()

    @classmethod
    def getRecHotData(cls, set_name, rec_no, expert_mode):
        return cls.sFilters[set_name].getRecHotData(rec_no, expert_mode)

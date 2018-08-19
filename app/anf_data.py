import logging
from StringIO import StringIO

from .data_a_json import DataSet_AJson
from search.cfg_flt_a_json import LEGEND_AJson
from search.hot_index import HotIndex

#===============================================
class AnfisaData:
    sSets = dict()
    sFilters = dict()
    sDefaultSetName = None

    @classmethod
    def setup(cls, config):
        for descr in config["datasets"]:
            set_name = descr["name"]
            if cls.sDefaultSetName is None:
                cls.sDefaultSetName = set_name
            if descr["kind"] == "a-json":
                cls.sSets[set_name] = DataSet_AJson(set_name, descr["file"])
            else:
                assert False
        for data_set in cls.sSets.values():
            data_set.testLegend(LEGEND_AJson)
        rep_out = StringIO()
        LEGEND_AJson.setup(rep_out)
        if not LEGEND_AJson.isOK():
            logging.fatal("FILTER LEGEND FAILED\n" + rep_out.gevalue())
        for name, data_set in cls.sSets.items():
            cls.sFilters[name] = HotIndex(data_set, LEGEND_AJson)
        logging.warning(LEGEND_AJson.getStatusInfo())

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

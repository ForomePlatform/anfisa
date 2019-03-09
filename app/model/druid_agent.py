from copy import deepcopy

from .rest import RestAgent
from .solutions import STD_XL_FILTERS
from app.model.a_config import AnfisaConfig
#===============================================
class DruidAgent:
    GRANULARITY = "all"
    INTERVAL = "2015-01-01/2015-12-31"

    sDefaultUrls = {
        "index": "http://localhost:8090/druid/indexer/v1/task",
        "query": "http://localhost:8082/druid/v2",
        "sql":   "http://localhost:8082/druid/v2/sql",
        "coord": "http://localhost:8081/druid/coordinator/v1"}

    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, config):
        druid_cfg = config.get("druid", dict())
        self.mRestAgents = {mode: RestAgent(druid_cfg.get(mode, url), mode)
            for mode, url in self.sDefaultUrls.items()}
        self.mFilters = {self.sStdFMark + flt_name: deepcopy(conditions)
            for flt_name, conditions in STD_XL_FILTERS}
        self.mVaultPrefix = druid_cfg["vault-prefix"]

    def call(self, mode, request_data, method = "POST", add_path = ""):
        return self.mRestAgents[mode].call(request_data, method, add_path)

    def getStdFilterNames(self):
        return self.mFilters.keys()

    def goodOpFilterName(self, flt_name):
        return (flt_name and not flt_name.startswith(self.sStdFMark)
            and flt_name[0].isalpha() and ' ' not in flt_name)

    def hasStdFilter(self, filter_name):
        return filter_name in self.mStdFilters

    def getStdFilterConditions(self, flt_name):
        return self.mFilters.get(flt_name)

    def normDataSetName(self, ds_name):
        if not self.mVaultPrefix:
            return ds_name
        assert not ds_name.startswith(self.mVaultPrefix)
        return self.mVaultPrefix + '.' + ds_name

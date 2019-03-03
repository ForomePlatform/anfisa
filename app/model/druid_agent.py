from copy import deepcopy

from .rest import RestAgent
from .solutions import STD_XL_FILTERS
#===============================================
class DruidAgent:
    GRANULARITY = "all"
    INTERVAL = "2015-01-01/2015-12-31"

    sDefaultUrls = {
        "index": "http://localhost:8090/druid/indexer/v1/task",
        "query": "http://localhost:8082/druid/v2",
        "sql":   "http://localhost:8082/druid/v2/sql",
        "coord": "http://localhost:8081/druid/coordinator/v1"}


    def __init__(self, config):
        druid_cfg = config.get("druid", dict())
        self.mRestAgents = {mode: RestAgent(druid_cfg.get(mode, url), mode)
            for mode, url in self.sDefaultUrls.items()}
        self.mFilters = deepcopy(STD_XL_FILTERS)
        self.mVaultPrefix = druid_cfg["vault-prefix"]

    def call(self, mode, request_data, method = "POST", add_path = ""):
        return self.mRestAgents[mode].call(request_data, method, add_path)

    def getStdFilterNames(self):
        return self.mFilters.keys()

    def hasStdFilter(self, flt_name):
        return flt_name in self.mFilters

    def getStdFilterConditions(self, flt_name):
        return self.mFilters.get(flt_name)

    def normDataSetName(self, ds_name):
        if not self.mVaultPrefix:
            return ds_name
        assert not ds_name.startswith(self.mVaultPrefix)
        return self.mVaultPrefix + '.' + ds_name

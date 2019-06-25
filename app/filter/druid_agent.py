from utils.rest import RestAgent
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
        self.mVaultPrefix = druid_cfg["vault-prefix"]

    def call(self, mode, request_data, method = "POST", add_path = ""):
        return self.mRestAgents[mode].call(request_data, method, add_path)

    def normDataSetName(self, ds_name):
        if not self.mVaultPrefix:
            return ds_name
        assert not ds_name.startswith(self.mVaultPrefix)
        return self.mVaultPrefix + '.' + ds_name

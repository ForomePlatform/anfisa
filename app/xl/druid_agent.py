#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from forome_tools.rest import RestAgent
#===============================================
class DruidAgent:
    GRANULARITY = "all"
    INTERVAL = "2015-01-01/2015-12-31"

    sDefaultUrls = {
        "index": "http://localhost:8081/druid/indexer/v1/task",
        "query": "http://localhost:8888/druid/v2",
        "sql":   "http://localhost:8888/druid/v2/sql",
        "coord": "http://localhost:8081/druid/coordinator/v1"}

    def __init__(self, config):
        druid_cfg = config.get("druid", dict())
        self.mRestAgents = {mode: RestAgent(druid_cfg.get(mode, url), mode)
            for mode, url in self.sDefaultUrls.items()}
        self.mVaultPrefix = druid_cfg["vault-prefix"]

    def call(self, mode, request_data, method = "POST",
            add_path = "", calm_mode = False):
        return self.mRestAgents[mode].call(request_data, method, add_path,
            calm_mode = calm_mode)

    def normDataSetName(self, ds_name):
        if not self.mVaultPrefix:
            return ds_name
        assert not ds_name.startswith(self.mVaultPrefix)
        return self.mVaultPrefix + '.' + ds_name

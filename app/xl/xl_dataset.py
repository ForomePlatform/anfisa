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

from time import time

from app.config.a_config import AnfisaConfig
from app.model.rest_api import RestAPI
from app.model.dataset import DataSet
from .xl_cond import XL_CondEnv
from .xl_unit import XL_Unit
from .xl_list import XlListTask
#===============================================
class XLDataset(DataSet):
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, data_vault, dataset_info, dataset_path):
        DataSet.__init__(self, data_vault, dataset_info, dataset_path)
        self.addModes({"XL"})
        self.mCondEnv = XL_CondEnv(self)
        self.mDruidAgent = self.getApp().getDruidAgent()
        self.getCondEnv().addMetaNumUnit("_ord")

        for unit_data in self.getFltSchema():
            if unit_data["kind"].startswith("transcript-"):
                continue
            if self.getCondEnv().nameIsReserved(unit_data["name"]):
                continue
            xl_unit = XL_Unit.create(self, unit_data)
            if xl_unit is not None:
                self._addUnit(xl_unit)
        self._setupUnits()

    def getDruidAgent(self):
        return self.mDruidAgent

    def getCondEnv(self):
        return self.mCondEnv

    def heavyMode(self):
        return True

    def _reportCounts(self, condition):
        return {"count": self.evalTotalCount(condition)}

    def makeSelectedStat(self, unit_names, condition, repr_context,
            flt_base_h, time_end, point_no = None):
        ret = []
        op_units = dict()
        for unit_h in flt_base_h.iterActiveOperativeUnits(point_no):
            op_units[unit_h.getName()] = unit_h
        for unit_name in unit_names:
            if unit_name in op_units:
                ret.append(op_units[unit_name].makeActiveStat(
                    condition, flt_base_h, repr_context))
            else:
                unit_h = self.getUnit(unit_name)
                assert not unit_h.isScreened()
                ret.append(unit_h.makeStat(condition, repr_context))
            if time_end is not None and time() > time_end:
                break
        return ret

    def evalTotalCount(self, condition = None):
        if condition is None:
            return self.getTotal()
        cond_repr = condition.getDruidRepr()
        if cond_repr is None:
            return self.getTotal()
        if cond_repr is False:
            return 0
        query = {
            "queryType": "timeseries",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                {"type": "count", "name": "count",
                    "fieldName": "_ord"}],
            "filter": condition.getDruidRepr(),
            "intervals": [self.mDruidAgent.INTERVAL]}
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return ret[0]["result"]["count"]

    def _evalRecSeq(self, condition, expect_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "search",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "granularity": self.mDruidAgent.GRANULARITY,
            "searchDimensions": ["_ord"],
            "limit": expect_count + 5,
            "intervals": [self.mDruidAgent.INTERVAL]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return [int(it["value"]) for it in ret[0]["result"]]

    def evalRecSeq(self, condition, expect_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "topN",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "dimension": "_ord",
            "threshold": expect_count + 5,
            "metric": "count",
            "granularity": self.mDruidAgent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": "_ord"}],
            "intervals": [self.mDruidAgent.INTERVAL]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        assert len(ret[0]["result"]) == expect_count
        return [int(it["_ord"]) for it in ret[0]["result"]]

    def evalSampleList(self, condition, max_count):
        if condition is None:
            cond_repr = None
        else:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
        query = {
            "queryType": "topN",
            "dataSource": self.mDruidAgent.normDataSetName(self.getName()),
            "dimension": "_ord",
            "threshold": max_count,
            "metric": "max_rand",
            "granularity": self.mDruidAgent.GRANULARITY,
            "aggregations": [{
                "type": "longMax", "name": "max_rand",
                "fieldName": "_rand"}],
            "intervals": [self.mDruidAgent.INTERVAL]}
        if cond_repr is not None:
            query["filter"] = cond_repr
        ret = self.mDruidAgent.call("query", query)
        assert len(ret) == 1
        return [int(it["_ord"]) for it in ret[0]["result"]]

    #===============================================
    def fiterRecords(self, condition, zone_data = None):
        assert zone_data is None
        rec_count = self.evalTotalCount(condition)
        assert rec_count <= AnfisaConfig.configOption("max.export.size")
        return self.evalRecSeq(condition, rec_count)

    #===============================================
    @RestAPI.xl_request
    def rq__xl_list(self, rq_args):
        if "dtree" in rq_args or "code" in rq_args:
            flt_base_h = self._getArgDTree(rq_args)
            condition = flt_base_h.getActualCondition(int(rq_args["no"]))
        else:
            flt_base_h = self._getArgCondFilter(rq_args)
            condition = flt_base_h.getCondition()
        return {"task_id": self.getApp().runTask(
            XlListTask(self, condition))}

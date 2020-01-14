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

import logging
from app.eval.var_unit import VarUnit, NumUnitSupport, EnumUnitSupport
#===============================================
class XL_Unit(VarUnit):
    def __init__(self, eval_space, descr, unit_kind = None):
        VarUnit.__init__(self, eval_space, descr, unit_kind)

    @staticmethod
    def create(eval_space, descr):
        if descr["kind"] == "numeric":
            return XL_NumUnit(eval_space, descr)
        ret = XL_EnumUnit(eval_space, descr)
        if ret.isDummy():
            return None
        return ret

#===============================================
class XL_NumUnit(XL_Unit, NumUnitSupport):
    def __init__(self, eval_space, descr):
        XL_Unit.__init__(self, eval_space, descr, "numeric")
        self.mDruidKind = "float" if self.getSubKind() == "float" else "long"

    def _makeStat(self, condition):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        druid_agent = self.getEvalSpace().getDruidAgent()
        query = {
            "queryType": "timeseries",
            "dataSource": druid_agent.normDataSetName(
                self.getEvalSpace().getName()),
            "granularity": druid_agent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                {"type": "count", "name": name_cnt,
                    "fieldName": self.getName()},
                {"type": "%sMin" % self.mDruidKind,
                    "name": name_min,
                    "fieldName": self.getName()},
                {"type": "%sMax" % self.mDruidKind,
                    "name": name_max,
                    "fieldName": self.getName()}],
            "intervals": [druid_agent.INTERVAL]}
        if condition is not None:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return [None, None, 0]
            if cond_repr is not None:
                query["filter"] = cond_repr
        rq = druid_agent.call("query", query)
        assert len(rq) == 1
        return [rq[0]["result"][nm] for nm in
            (name_min, name_max, name_cnt)]

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        vmin, vmax, count = self._makeStat(condition)
        ret_handle["count"] = count
        if count > 0:
            ret_handle["min"] = vmin
            ret_handle["max"] = vmax
        return ret_handle

#===============================================
class XL_EnumUnit(XL_Unit, EnumUnitSupport):
    def __init__(self, eval_space, descr):
        XL_Unit.__init__(self, eval_space, descr, "enum")
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum(info[1]
            for info in descr["variants"])

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def _makeStat(self, condition):
        druid_agent = self.getEvalSpace().getDruidAgent()
        query = {
            "queryType": "topN",
            "dataSource": druid_agent.normDataSetName(
                self.getEvalSpace().getName()),
            "dimension": self.getName(),
            "threshold": len(self.mVariants) + 5,
            "metric": "count",
            "granularity": druid_agent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getName()}],
            "intervals": [druid_agent.INTERVAL]}
        if condition is not None:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return []
            if cond_repr is not None:
                query["filter"] = cond_repr
        rq = druid_agent.call("query", query)
        if len(rq) != 1:
            logging.error("Got problem with xl_unit %s: %d" %
                (self.getName(), len(rq)))
            if len(rq) == 0:
                return [[var, 0] for var in self.mVariants]

        assert len(rq) == 1
        counts = dict()
        for rec in rq[0]["result"]:
            counts[rec[self.getName()]] = rec["count"]
        return [[var, counts.get(var, 0)]
            for var in self.mVariants]

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        ret_handle["variants"] = self._makeStat(condition)
        return ret_handle

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
from forome_tools.variants import VariantSet
from app.eval.var_unit import VarUnit, NumUnitSupport, EnumUnitSupport
from app.ws.val_stat import NumHistogramBuilder
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

    def _makeQuery(self, druid_agent, condition):
        query = {
            "queryType": "timeseries",
            "dataSource": druid_agent.normDataSetName(
                self.getEvalSpace().getName()),
            "granularity": druid_agent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                {
                    "type": "count", "name": "__count",
                    "fieldName": self.getInternalName()},
                {
                    "type": "%sMin" % self.mDruidKind,
                    "name": "__min",
                    "fieldName": self.getInternalName()},
                {
                    "type": "%sMax" % self.mDruidKind,
                    "name": "__max",
                    "fieldName": self.getInternalName()}],
            "intervals": [druid_agent.INTERVAL]}
        if condition is not None:
            cond_repr = condition.getDruidRepr()
            if cond_repr is False:
                return None
            if cond_repr is not None:
                query["filter"] = cond_repr
        return query

    def _prepareHistogram(self, druid_agent, query, v_min, v_max, count):
        if self.getEvalSpace().noHistogram():
            return None
        h_builder = NumHistogramBuilder(v_min, v_max, count, self)
        h_info = h_builder.getInfo()
        if h_info is None:
            return None
        query["aggregations"] = [{
            "type": "quantilesDoublesSketch",
            "name": "__sketch__",
            "fieldName": self.getInternalName(),
            "k": 128}]
        query["postAggregations"] = [
            {
                "type": "quantilesDoublesSketchToHistogram",
                "name": "__hist",
                "field": {
                    "type": "fieldAccess",
                    "name": "__sketch",
                    "splitPoints": h_builder.getIntervals(),
                    "numBins": len(h_builder.getIntervals()) + 1,
                    "fieldName": "__sketch__"},
            }]
        if h_builder.getIntMode():
            (query["postAggregations"][0]
                ["numBins"]) = len(h_builder.getIntervals()) + 1
        else:
            (query["postAggregations"][0]
                ["splitPoints"]) = h_builder.getIntervals()

        rq = druid_agent.call("query", query)
        h_info[3] = rq[0]["result"]["__hist"]
        return h_info

    def makeStat(self, condition, eval_h):
        druid_agent = self.getEvalSpace().getDruidAgent()
        query = self._makeQuery(druid_agent, condition)
        if query is not None:
            rq = druid_agent.call("query", query)
            v_min, v_max, count = [rq[0]["result"][nm] for nm in
                ("__min", "__max", "__count")]
        else:
            v_min, v_max, count = None, None, 0
        h_info = self._prepareHistogram(
            druid_agent, query, v_min, v_max, count)
        ret_handle = self.prepareStat()
        ret_handle["counts"] = [count]
        if h_info is not None:
            ret_handle["histogram"] = h_info
        if count > 0:
            ret_handle["min"] = v_min
            ret_handle["max"] = v_max

        return ret_handle

#===============================================
class XL_EnumUnit(XL_Unit, EnumUnitSupport):
    def __init__(self, eval_space, descr):
        XL_Unit.__init__(self, eval_space, descr, "enum")
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum(info[1]
            for info in descr["variants"])
        self.mVariantSet = VariantSet(self.mVariants)

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def getVariantSet(self):
        return self.mVariantSet

    def _makeStat(self, condition):
        druid_agent = self.getEvalSpace().getDruidAgent()
        query = {
            "queryType": "topN",
            "dataSource": druid_agent.normDataSetName(
                self.getEvalSpace().getName()),
            "dimension": self.getInternalName(),
            "threshold": len(self.mVariants) + 5,
            "metric": "count",
            "granularity": druid_agent.GRANULARITY,
            "aggregations": [{
                "type": "count", "name": "count",
                "fieldName": self.getInternalName()}],
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
                (self.getInternalName(), len(rq)))
            if len(rq) == 0:
                return [[var, 0] for var in self.mVariants]

        assert len(rq) == 1
        counts = dict()
        for rec in rq[0]["result"]:
            counts[rec[self.getInternalName()]] = rec["count"]
        return [[var, counts.get(var, 0)]
            for var in self.mVariants]

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        ret_handle["variants"] = self._makeStat(condition)
        return ret_handle

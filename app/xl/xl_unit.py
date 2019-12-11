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
from app.filter.unit import Unit
from app.model.zygosity import ZygosityComplex
#===============================================
class XL_Unit(Unit):
    def __init__(self, dataset_h, descr, unit_kind = None):
        Unit.__init__(self, descr, unit_kind)
        self.mDruidKind = descr["kind"]
        self.mDataSet = dataset_h

    def getDS(self):
        return self.mDataSet

    def getCondEnv(self):
        return self.mDataSet.getCondEnv()

    def getDruidKind(self):
        return self.mDruidKind

    def isDetailed(self):
        return False

    @staticmethod
    def create(dataset_h, descr):
        if descr["kind"] == "zygosity":
            ret = XL_ZygosityUnit(dataset_h, descr)
            return None if ret.isDummy() else ret
        if descr["kind"] in {"long", "float"}:
            return XL_NumUnit(dataset_h, descr)
        ret = XL_EnumUnit(dataset_h, descr)
        if ret.isDummy():
            return None
        return ret

#===============================================
class XL_NumUnit(XL_Unit):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr)
        self.getDS().getCondEnv().addNumUnit(self)

    def _makeStat(self, condition):
        name_cnt = "_cnt_%d" % self.getNo()
        name_min = "_min_%d" % self.getNo()
        name_max = "_max_%d" % self.getNo()
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "timeseries",
            "dataSource": druid_agent.normDataSetName(self.getDS().getName()),
            "granularity": druid_agent.GRANULARITY,
            "descending": "true",
            "aggregations": [
                {"type": "count", "name": name_cnt,
                    "fieldName": self.getName()},
                {"type": "%sMin" % self.getDruidKind(),
                    "name": name_min,
                    "fieldName": self.getName()},
                {"type": "%sMax" % self.getDruidKind(),
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

    def makeStat(self, condition, repr_context = None):
        ret = self.prepareStat()
        vmin, vmax, count = self._makeStat(condition)
        if count == 0:
            vmin, vmax = None, None
        return ret + [vmin, vmax, count, 0]

    def parseCondition(self, cond_info):
        assert cond_info[0] == "numeric"
        assert cond_info[1] == self.getName()
        bounds, use_undef = cond_info[2:]
        return self.getCondEnv().makeNumericCond(self, bounds, use_undef)

#===============================================
class XL_EnumUnit(XL_Unit):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr,
            "status" if descr.get("atomic") else "enum")
        self.mVariants = [info[0]
            for info in descr["variants"]]
        self.mAccumCount = sum(info[1]
            for info in descr["variants"])
        self.getDS().getCondEnv().addEnumUnit(self)

    def isDummy(self):
        return len(self.mVariants) < 1 or self.mAccumCount == 0

    def _makeStat(self, condition):
        druid_agent = self.getDS().getDruidAgent()
        query = {
            "queryType": "topN",
            "dataSource": druid_agent.normDataSetName(self.getDS().getName()),
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

    def makeStat(self, condition, repr_context = None):
        ret = self.prepareStat()
        ret.append(self._makeStat(condition))
        return ret

    def parseCondition(self, cond_info):
        assert cond_info[0] == "enum"
        assert cond_info[1] == self.getName()
        filter_mode, variants = cond_info[2:]
        return self.getCondEnv().makeEnumCond(
            self, variants, filter_mode)

#===============================================
class XL_ZygosityUnit(XL_Unit, ZygosityComplex):
    def __init__(self, dataset_h, descr):
        XL_Unit.__init__(self, dataset_h, descr)
        ZygosityComplex.__init__(self,
            dataset_h.getFamilyInfo(), descr)

        fam_units = []
        for fam_name in self.iterFamNames():
            fam_units.append(
                self.getDS().getCondEnv().addMetaNumUnit(fam_name))
        self.getDS().getCondEnv().addSpecialUnit(self)
        self.setupSubUnits(fam_units)

    def setup(self):
        self.setupXCond()

    def isDummy(self):
        return not self.isOK()

    def makeStat(self, condition, repr_context = None):
        return ZygosityComplex.makeStat(self, self.getDS(),
            condition, repr_context)

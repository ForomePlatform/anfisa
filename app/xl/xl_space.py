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

from app.eval.eval_space import (EvalSpace, Eval_Condition,
    CondSupport_None, CondSupport_All)
from app.eval.var_unit import ReservedNumUnit
from app.eval.condition import ConditionMaker, ZYG_BOUNDS_VAL
#===============================================
class XL_EvalSpace(EvalSpace):
    def __init__(self, ds_h, druid_agent):
        EvalSpace.__init__(self, ds_h)
        self.mDruidAgent = druid_agent
        self.mTotalCounts = [ds_h.getTotal()]
        self.mNoHistogram = (ds_h.getApp().getOption("druid.no.histogram") is True)

        self.mRandRUnit = ReservedNumUnit(self, "_rand")
        self._addReservedUnit(self.mRandRUnit)
        self.mOrdRUnit = ReservedNumUnit(self, "_ord")
        self._addReservedUnit(self.mOrdRUnit)
        self.mZygRUnits = []

    def _addZygUnit(self, zyg_name):
        r_unit_h = ReservedNumUnit(self, zyg_name)
        self.mZygRUnits.append(r_unit_h)
        self._addReservedUnit(r_unit_h)

    def getCondKind(self):
        return "xl"

    def getCondNone(self):
        return XL_None(self)

    def getCondAll(self):
        return XL_All(self)

    def makeEmptyCounts(self):
        return [0]

    def getTotalCounts(self):
        return self.mTotalCounts

    def isDetailed(self):
        return False

    def getDruidAgent(self):
        return self.mDruidAgent

    def heavyMode(self):
        return True

    def getZygUnit(self, idx):
        return self.mZygRUnits[idx]

    def iterZygUnits(self):
        return iter(self.mZygRUnits)

    def noHistogram(self):
        return self.mNoHistogram

    def makeNumericCond(self, unit_h, min_val = None, min_eq = True,
            max_val = None, max_eq = True,  zyg_bounds = None):
        if min_val is not None or max_val is not None:
            assert zyg_bounds is None
        else:
            min_val, min_eq, max_val, max_eq = ZYG_BOUNDS_VAL[zyg_bounds]
        return XL_NumCondition(self, unit_h,
            [min_val, min_eq, max_val, max_eq])

    def makeEnumCond(self, unit_h, variants, filter_mode = ""):
        if len(variants) == 0:
            return XL_All() if filter_mode == "NOT" else XL_None()
        if filter_mode == "AND":
            return self.joinAnd([XL_EnumSingleCondition(self,
                unit_h, variant) for variant in variants])
        if len(variants) == 1:
            cond = XL_EnumSingleCondition(self, unit_h, variants[0])
        else:
            cond = XL_EnumInCondition(self, unit_h, variants)
        if filter_mode == "NOT":
            return cond.negative()
        return cond

    def evalTotalCounts(self, condition = None):
        if condition is None:
            return self.getTotalCounts()
        cond_repr = condition.getDruidRepr()
        if cond_repr is None:
            return self.getTotalCounts()
        if cond_repr is False:
            return [0]
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
        return [ret[0]["result"]["count"]]

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
class XL_Condition(Eval_Condition):
    def __init__(self, eval_space, cond_type):
        Eval_Condition.__init__(self, eval_space, cond_type)

    def _makeOr(self, other):
        return XL_Or([self, other])

    def _makeAnd(self, other):
        return XL_And([self, other])

    def negative(self):
        return XL_Negation(self)

    def getDruidRepr(self):
        assert False

#===============================================
class XL_NumCondition(XL_Condition):
    def __init__(self, eval_space, unit_h, bounds):
        XL_Condition.__init__(self, eval_space, "numeric")
        self.mUnitH = unit_h
        self.mBounds = bounds
        self.mData = [unit_h.getName()] + list(bounds)

    def getData(self):
        return self.mData

    def getDruidRepr(self):
        ret = {
            "dimension": self.mUnitH.getInternalName(),
            "type": "bound",
            "lowerStrict": not self.mBounds[1],
            "upperStrict": not self.mBounds[3],
            "ordering": "numeric"}
        if self.mBounds[0] is not None:
            ret["lower"] = str(self.mBounds[0])
        if self.mBounds[2] is not None:
            ret["upper"] = str(self.mBounds[2])
        return ret

    def toJSon(self):
        return ConditionMaker.condNum(*self.mData)

#===============================================
class XL_EnumSingleCondition(XL_Condition):
    def __init__(self, eval_space, unit_h, variant):
        XL_Condition.__init__(self, eval_space, "enum-single")
        self.mUnitH = unit_h
        self.mVariant = variant
        self.mData = [unit_h.getName(), [variant]]

    def getData(self):
        return self.mData

    def toJSon(self):
        return ConditionMaker.condEnum(*self.mData)

    def getDruidRepr(self):
        return {
            "type": "selector",
            "dimension": self.mUnitH.getInternalName(),
            "value": self.mVariant}

#===============================================
class XL_EnumInCondition(XL_Condition):
    def __init__(self, eval_space, unit_h, variants):
        XL_Condition.__init__(self, eval_space, "enum-in")
        self.mUnitH = unit_h
        self.mVariants = sorted(variants)
        self.mData = [unit_h.getName(), self.mVariants]

    def getData(self):
        return self.mData

    def toJSon(self):
        return ConditionMaker.condEnum(*self.mData)

    def getDruidRepr(self):
        return {
            "type": "in",
            "dimension": self.mUnitH.getInternalName(),
            "values": self.mVariants}

#===============================================
class XL_Negation(XL_Condition):
    def __init__(self, base_cond):
        XL_Condition.__init__(self, base_cond.getEvalSpace(), "neg")
        self.mBaseCond = base_cond

    def toJSon(self):
        return ConditionMaker.condNot(self.mBaseCond.toJSon())

    def negative(self):
        return self.mBaseCond

    def isPositive(self):
        return False

    def getDruidRepr(self):
        return {
            "type": "not",
            "field": self.mBaseCond.getDruidRepr()}

#===============================================
class _XL_Joiner(XL_Condition):
    def __init__(self, items, cond_type):
        XL_Condition.__init__(self, items[0].getEvalSpace(), cond_type)
        self.mItems = items

    def getItems(self):
        return self.mItems

    def getDruidRepr(self):
        return {
            "type": self.getCondType(),
            "fields": [cond.getDruidRepr() for cond in self.mItems]}

    def visit(self, visitor):
        if visitor.lookAt(self):
            for it in self.mItems:
                it.visit(visitor)

#===============================================
class XL_And(_XL_Joiner):
    def __init__(self, items):
        _XL_Joiner.__init__(self, items, "and")

    def toJSon(self):
        return ConditionMaker.joinAnd(
            [it.toJSon() for it in self.getItems()])

    def addAnd(self, other):
        if other.getCondType() == "null":
            return other
        if other.getCondType() == "all":
            return self
        if other.getCondType() == "and":
            add_items = other.getItems()
        else:
            add_items = [other]
        return XL_And(self.getItems() + add_items)

#===============================================
class XL_Or(_XL_Joiner):
    def __init__(self, items):
        _XL_Joiner.__init__(self, items, "or")

    def toJSon(self):
        return ConditionMaker.joinOr(
            [it.toJSon() for it in self.getItems()])

    def addOr(self, other):
        if other.getCondType() == "null":
            return self
        if other.getCondType() == "all":
            return other
        if other.getCondType() == "or":
            add_items = other.getItems()
        else:
            add_items = [other]
        return XL_Or(self.getItems() + add_items)

#===============================================
class XL_None(XL_Condition, CondSupport_None):
    def __init__(self, eval_space):
        XL_Condition.__init__(self, eval_space, "null")

    def getDruidRepr(self):
        return False

    def isPositive(self):
        return False

    def negative(self):
        return XL_All(self.getEvalSpace())

#===============================================
class XL_All(XL_Condition, CondSupport_All):
    def __init__(self, eval_space):
        XL_Condition.__init__(self, eval_space, "all")

    def getDruidRepr(self):
        return None

    def negative(self):
        return XL_None(self.getEvalSpace())

#===============================================

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

from app.filter.cond_env import CondEnv
from app.filter.unit import MetaUnit
#===============================================
class XL_CondEnv(CondEnv):
    def __init__(self, ds_h):
        CondEnv.__init__(self, ds_h.getName(), ds_h)

    def getCondKind(self):
        return "xl"

    def getCondNone(self):
        return XL_None(self)

    def getCondAll(self):
        return XL_All(self)

    def addMetaNumUnit(self, name):
        unit_h = MetaUnit(name, "num")
        self.addReservedUnit(unit_h)
        return unit_h

    def makeNumericCond(self, unit_h, bounds, use_undef = None):
        return XL_NumCondition(self, unit_h.getName(), bounds, use_undef)

    def makeEnumCond(self, unit_h, variants, filter_mode = ""):
        if len(variants) == 0:
            return XL_All() if filter_mode == "NOT" else XL_None()
        if filter_mode == "AND":
            return self.joinAnd([XL_EnumSingleCondition(self,
                unit_h.getName(), variant) for variant in variants])
        if len(variants) == 1:
            cond = XL_EnumSingleCondition(self, unit_h.getName(), variants[0])
        else:
            cond = XL_EnumInCondition(self, unit_h.getName(), variants)
        if filter_mode == "NOT":
            return cond.negative()
        return cond

#===============================================
class XL_Condition:
    def __init__(self, cond_env, cond_type):
        self.mCondEnv = cond_env
        self.mCondType = cond_type

    def getCondEnv(self):
        return self.mCondEnv

    def getCondType(self):
        return self.mCondType

    def __not__(self):
        assert False

    def __and__(self, other):
        assert False

    def __or__(self, other):
        assert False

    def addOr(self, other):
        assert other is not None and other.getCondType() is not None
        if other.getCondType() == "or":
            return other.addOr(self)
        elif other.getCondType() == "null":
            return self
        elif other.getCondType() == "all":
            return other
        return XL_Or([self, other])

    def addAnd(self, other):
        assert other is not None and other.getCondType() is not None
        if other.getCondType() == "and":
            return other.addAnd(self)
        elif other.getCondType() == "all":
            return self
        elif other.getCondType() == "null":
            return other
        return XL_And([self, other])

    def negative(self):
        return XL_Negation(self)

    def getDruidRepr(self):
        assert False

#===============================================
class XL_NumCondition(XL_Condition):
    def __init__(self, cond_env, unit_name, bounds, use_undef = False):
        XL_Condition.__init__(self, cond_env, "num")
        self.mUnitName = unit_name
        self.mBounds = bounds
        self.mUseUndef = use_undef

    def getDruidRepr(self):
        # use_undef ignored
        ret = {
            "dimension": self.mUnitName,
            "type": "bound",
            "lowerStrict": False,
            "upperStrict": False,
            "ordering": "numeric"}
        if self.mBounds[0] is not None:
            ret["lower"] = str(self.mBounds[0])
        if self.mBounds[1] is not None:
            ret["upper"] = str(self.mBounds[1])
        return ret

#===============================================
class XL_EnumSingleCondition(XL_Condition):
    def __init__(self, cond_env, unit_name, variant):
        XL_Condition.__init__(self, cond_env, "enum-single")
        self.mUnitName = unit_name
        self.mVariant = variant

    def getDruidRepr(self):
        return {
            "type": "selector",
            "dimension": self.mUnitName,
            "value": self.mVariant}

#===============================================
class XL_EnumInCondition(XL_Condition):
    def __init__(self, cond_env, unit_name, variants):
        XL_Condition.__init__(self, cond_env, "enum-in")
        self.mUnitName = unit_name
        self.mVariants = sorted(variants)

    def getDruidRepr(self):
        return {
            "type": "in",
            "dimension": self.mUnitName,
            "values": self.mVariants}

#===============================================
class XL_Negation(XL_Condition):
    def __init__(self, base_cond):
        XL_Condition.__init__(self, base_cond.getCondEnv(), "neg")
        self.mBaseCond = base_cond

    def negative(self):
        return self.mBaseCond

    def getDruidRepr(self):
        return {
            "type": "not",
            "field": self.mBaseCond.getDruidRepr()}

#===============================================
class _XL_Joiner(XL_Condition):
    def __init__(self, items, cond_type):
        XL_Condition.__init__(self, items[0].getCondEnv(), cond_type)
        self.mItems = items

    def getItems(self):
        return self.mItems

    def getDruidRepr(self):
        return {
            "type": self.getCondType(),
            "fields": [cond.getDruidRepr() for cond in self.mItems]}

#===============================================
class XL_And(_XL_Joiner):
    def __init__(self, items):
        _XL_Joiner.__init__(self, items, "and")

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
class XL_None(XL_Condition):
    def __init__(self, cond_env):
        XL_Condition.__init__(self, cond_env, "null")

    def addAnd(self, other):
        return self

    def addOr(self, other):
        return other

    def negative(self):
        return XL_All()

    def getDruidRepr(self):
        return False

#===============================================
class XL_All(XL_Condition):
    def __init__(self, cond_env):
        XL_Condition.__init__(self, cond_env, "all")

    def addAnd(self, other):
        return other

    def addOr(self, other):
        return self

    def negative(self):
        return XL_None()

    def getDruidRepr(self):
        return None

#===============================================

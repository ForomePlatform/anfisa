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

import abc
from copy import deepcopy

#===============================================
class VarUnit:
    def __init__(self, eval_space, descr, unit_kind = None,
            sub_kind = None):
        self.mEvalSpace = eval_space
        self.mDescr = descr
        self.mUnitKind  = descr.get("kind", unit_kind)
        self.mSubKind = descr.get("sub-kind", sub_kind)
        self.mInternalName = descr["name"]
        self.mVGroup = descr.get("vgroup")
        self.mNo    = descr.get("no", -1)
        self.mScreened = False
        if unit_kind is not None:
            assert self.mUnitKind == unit_kind, (
                f"Kind conflict: {self.mUnitKind}/{unit_kind} "
                f"for {self.mInternalName}")
        if sub_kind is not None:
            assert self.mSubKind == sub_kind, (
                f"Sub-kind conflict: {self.mSubKind}/{sub_kind}"
                f"for {self.mInternalName}")

        var_kind, var_descr = (self.mEvalSpace.getDS().
            getDataVault().getVariableInfo(self.mInternalName))

        assert self.mUnitKind == var_kind, (
            f"Variable kind conflict: {self.mUnitKind}/{var_kind} "
                f"for {self.mInternalName}")

        self.mInfo = deepcopy(var_descr)
        self.mName = self.mInfo["name"].replace(' ', '_')
        self.mInfo["vgroup"] = self.mVGroup
        self.mInfo["kind"] = self.mUnitKind
        if self.mSubKind:
            self.mInfo["sub-kind"] = self.mSubKind

    def getEvalSpace(self):
        return self.mEvalSpace

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def getInternalName(self):
        return self.mInternalName

    def getDescr(self):
        return self.mDescr

    def getInfo(self):
        return self.mInfo

    def getVGroup(self):
        return self.mVGroup

    def getSubKind(self):
        return self.mSubKind

    def getNo(self):
        return self.mNo

    def isScreened(self):
        return self.mScreened

    def isDetailed(self):
        return False

    def isInDTrees(self):
        return True

    def _setScreened(self, value = True):
        self.mScreened = value

    def prepareStat(self, incomplete_mode = False):
        ret_handle = deepcopy(self.mInfo)
        if incomplete_mode:
            ret_handle["incomplete"] = True
        return ret_handle

#===============================================
#===============================================
class NumUnitSupport:
    def buildCondition(self, cond_data, eval_h):
        min_val, min_eq, max_val, max_eq = cond_data[2]
        return self.getEvalSpace().makeNumericCond(self,
            min_val, min_eq, max_val, max_eq)

#===============================================
class EnumUnitSupport:
    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]
        if len(variants) == 0:
            eval_h.operationError(cond_data,
                f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()
        return self.getEvalSpace().makeEnumCond(
            self, variants, filter_mode)

#===============================================
#===============================================
class ComplexEnumUnit(VarUnit, EnumUnitSupport):
    def __init__(self, eval_space, descr,
            unit_kind = None, sub_kind = None):
        VarUnit.__init__(self, eval_space, descr, unit_kind, sub_kind)

    @abc.abstractmethod
    def iterComplexCriteria(self, context = None, variants = None):
        pass

    def collectComplexStat(self, ret_handle, base_condition,
            context = None, detailed = False):
        val_stat_list = []
        for name, condition in self.iterComplexCriteria(context):
            if base_condition is not None:
                condition = condition.addAnd(base_condition)
            info = [name] + self.getEvalSpace().evalTotalCounts(condition)
            if not detailed:
                info = info[:2]
            val_stat_list.append(info)
        if detailed:
            ret_handle["detailed"] = True
        ret_handle["variants"] = val_stat_list

    def buildCondition(self, cond_data, eval_h, context = None):
        filter_mode, variants = cond_data[2:4]
        single_cr_seq = []
        for _, condition in self.iterComplexCriteria(context, variants):
            single_cr_seq.append(condition)
        if filter_mode == "NOT":
            return self.getEvalSpace().joinAnd(
                [cond.negative() for cond in single_cr_seq])
        if filter_mode == "AND":
            return self.getEvalSpace().joinAnd(single_cr_seq)
        return self.getEvalSpace().joinOr(single_cr_seq)

#===============================================
class FunctionUnit(ComplexEnumUnit):
    def __init__(self, eval_space, descr, sub_kind, parameters):
        ComplexEnumUnit.__init__(self, eval_space, descr,
            unit_kind = "func", sub_kind = sub_kind)
        self.mParameters = parameters

    def getParameters(self):
        return self.mParameters

    def makeInfoStat(self, eval_h):
        return VarUnit.prepareStat(self, None)

    @abc.abstractmethod
    def locateContext(self, cond_data, eval_h):
        return None

    @abc.abstractmethod
    def makeParamStat(self, condition, parameters, eval_h):
        return None

    @abc.abstractmethod
    def validateArgs(self, func_args):
        assert False

    def buildCondition(self, cond_data, eval_h):
        context = self.locateContext(cond_data, eval_h)
        return ComplexEnumUnit.buildCondition(self,
            cond_data, eval_h, context)

#===============================================
#===============================================
class ReservedNumUnit(NumUnitSupport):
    def __init__(self, eval_space, name, sub_kind = "int"):
        self.mEvalSpace = eval_space
        self.mName = name
        self.mSubKind = sub_kind

    def getUnitKind(self):
        return "numeric"

    def getName(self):
        return self.mName

    def getInternalName(self):
        return self.mName

    def getEvalSpace(self):
        return self.mEvalSpace

    def getSubKind(self):
        return self.mSubKind

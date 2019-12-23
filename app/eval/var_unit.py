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
from .condition import validateNumCondition, validateEnumCondition

#===============================================
class VarUnit:
    def __init__(self, eval_space, descr, unit_kind = None, sub_kind = None):
        self.mEvalSpace = eval_space
        self.mDescr = descr
        self.mUnitKind  = descr["kind"] if unit_kind is None else unit_kind
        self.mSubKind = descr.get("sub-kind") if sub_kind is None else sub_kind
        self.mName  = descr["name"]
        self.mTitle = descr["title"]
        self.mNo    = descr.get("no", -1)
        self.mVGroup = descr.get("vgroup")
        self.mRenderMode = descr.get("render")
        self.mToolTip = descr.get("tooltip")
        self.mScreened = False

    def getEvalSpace(self):
        return self.mEvalSpace

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def getDescr(self):
        return self.mDescr

    def getTitle(self):
        return self.mTitle

    def getVGroup(self):
        return self.mVGroup

    def getToolTip(self):
        return self.mToolTip

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

    def prepareStat(self, incomplete_eval_h = None):
        ret_handle = {
            "kind": self.mUnitKind,
            "name": self.mName,
            "vgroup": self.mVGroup}
        if self.mSubKind:
            ret_handle["sub-kind"] = self.mSubKind
        if self.mTitle and self.mTitle != self.mName:
            ret_handle["title"] = self.mTitle
        if self.mRenderMode:
            ret_handle["render"] = self.mRenderMode
        if self.mToolTip:
            ret_handle["tooltip"] = self.mToolTip
        if incomplete_eval_h is not None:
            ret_handle["incomplete"] = True
        return ret_handle

#===============================================
#===============================================
class NumUnitSupport:
    def validateCondition(self, cond_info, op_units):
        return validateNumCondition(cond_info)

    def parseCondition(self, cond_info, eval_h):
        min_val, min_eq, max_val, max_eq = cond_info[2]
        return self.getEvalSpace().makeNumericCond(self,
            min_val, min_eq, max_val, max_eq)

#===============================================
class EnumUnitSupport:
    def validateCondition(self, cond_info, op_units):
        return validateEnumCondition(cond_info)

    def parseCondition(self, cond_info, eval_h):
        filter_mode, variants = cond_info[2:]
        return self.getEvalSpace().makeEnumCond(
            self, variants, filter_mode)

#===============================================
#===============================================
class ReservedNumUnit(NumUnitSupport):
    def __init__(self, eval_space, name, sub_kind = "int"):
        self.mEvalSpace = eval_space
        self.mName = name
        self.mSubKind = sub_kind

    def getName(self):
        return self.mName

    def getEvalSpace(self):
        return self.mEvalSpace

    def getSubKind(self):
        return self.mSubKind

#===============================================
class ComplexEnumUnit(VarUnit, EnumUnitSupport):
    def __init__(self, eval_space, descr,
            unit_kind = None, sub_kind = None):
        VarUnit.__init__(self, eval_space, descr, unit_kind, sub_kind)

    @abc.abstractmethod
    def iterComplexCriteria(self, context = None, variants = None):
        pass

    @abc.abstractmethod
    def locateContext(self, eval_h):
        pass

    def collectComplexStat(self, ret_handle, base_condition,
            context = None, detailed = False):
        val_stat_list = []
        for name, condition in self.iterComplexCriteria(context):
            if base_condition is not None:
                condition = condition.addAnd(base_condition)
            info = [name, self.getEvalSpace().evalTotalCount(condition)]
            if detailed:
                info.insert(1, self.getEvalSpace().evalDetailedTotalCount(
                    condition))
            val_stat_list.append(info)
        if detailed:
            ret_handle["detailed"] = True
        ret_handle["variants"] = val_stat_list

    def parseCondition(self, cond_data, eval_h):
        context = self.locateContext(cond_data, eval_h)
        filter_mode, variants = cond_data[-2:]
        single_cr_seq = []
        for _, condition in self.iterComplexCriteria(context, variants):
            single_cr_seq.append(condition)
        if filter_mode == "NOT":
            return self.getEvalSpace().joinAnd(
                [cond.negative() for cond in single_cr_seq])
        if filter_mode == "AND":
            return self.getEvalSpace().joinAnd(single_cr_seq)
        return self.getEvalSpace().joinOr(single_cr_seq)

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
    def __init__(self, eval_space, descr, unit_kind = None, sub_kind = None):
        self.mEvalSpace = eval_space
        self.mDescr = descr
        self.mUnitKind = descr.get("kind", unit_kind)
        self.mSubKind = descr.get("sub-kind", sub_kind)
        self.mInternalName = descr["name"]
        self.mVGroup = descr.get("vgroup")
        self.mNo = descr.get("no", -1)
        self.mDimName = descr.get("dim-name")
        self.mScreened = False
        if unit_kind is not None:
            assert self.mUnitKind == unit_kind, (
                f"Kind conflict: {self.mUnitKind}/{unit_kind} "
                f"for {self.mInternalName}")
        if sub_kind is not None:
            assert self.mSubKind == sub_kind, (
                f"Sub-kind conflict: {self.mSubKind}/{sub_kind}"
                f" for {self.mInternalName}")

        self.mVarDescr = self.mEvalSpace.getVarRegistry()[self.mInternalName]

        self.mName = self.mVarDescr["attribute"]

        self.mPresentationInfo = {
            "name":     self.mName,
            "vgroup":   self.mVGroup,
            "kind":     self.mUnitKind
        }
        self.addPresentationProperty("sub-kind", self.mSubKind)
        self.addPresentationProperty("classes",
            self.mVarDescr.get("facets"))
        self.addPresentationProperty("tooltip",
            self.mVarDescr.get("description"))
        self.addPresentationProperty("render-mode",
            self.mVarDescr.get("render"))

        var_type = self.mVarDescr["type"]
        sub_kind = self.mSubKind
        if var_type == "func":
            assert self.mUnitKind == "func", (
                f"Variable {self.mName} func kind conflict: " +
                f"{var_type} vs {self.mUnitKind}")
            return

        var_mean = self.mDescr.get("mean")
        var_transcript= False
        if self.mSubKind and self.mSubKind.startswith("transcript-"):
            assert (self.mVarDescr.get("transcript-mode") or
                self.mVarDescr.get("transcript-mode-flex")), (
                f"Variable {self.mName} transcript kind conflict: " +
                f"{self.mSubKind} /{self.mInternalName}")
            sub_kind = self.mSubKind[11:]
            var_transcript = True
            if sub_kind == "multiset" and var_type == "panel":
                var_type = "multiset"
            assert var_type == "variety" or sub_kind == var_type, (
                f"Variable {self.mName} transcript subkind conflict: " +
                f"{self.mSubKind} vs {var_type}")
            assert var_mean in (None, "pre-variety", "variety", "panel"), (
                f"Variable {self.mName} extra mean: {var_mean}")
        else:
            assert (not self.mVarDescr.get("transcript-mode") or
                self.mVarDescr.get("transcript-mode-flex")), (
                f"Variable {self.mName} no-transcript kind conflict: " +
                f"{self.mSubKind} vs {var_type}")

        if var_mean == "pre-variety":
            self.mName = self.mInternalName

        if var_mean is not None:
            check_mean = {
                "presence":     "presence",
                "panel":        "panel",
                "variety":      "variety",
                "pre-variety":  "variety"}.get(var_mean)
            if var_transcript and var_mean == "panel":
                check_mean = "multiset"
            assert check_mean == var_type, (
                f"Variable {self.mName} mean conflict: " +
                f"{var_mean} for {var_type}")
        else:
            assert var_type not in {"presence"}, (
                f"Variable {self.mName} extra mean conflict for {var_type}")

        if self.mUnitKind == "numeric":
            assert sub_kind == var_type, (
                f"Variable {self.mName} numeric kind conflict: " +
                f"{var_type} vs {self.mSubKind}")
        else:
            assert self.mUnitKind == "enum"
            assert sub_kind in ("status", "multi", "multiset",
                "panel", "presence", "variety"), sub_kind
            assert var_type in {"status", "multiset",
                "panel", "presence", "variety"}, (
                f"Variable {self.mName} enum kind conflict: " +
                f"{var_type} vs {self.mUnitKind}")
            if not self.mPresentationInfo.get("render-mode"):
                self.mPresentationInfo["render-mode"] = (
                    "tree-map" if var_type == "variety"
                    else "pie" if sub_kind == "status"
                    else "bar")

    def addPresentationProperty(self, val, value):
        if value is not None:
            self.mPresentationInfo[val] = value

    def getEvalSpace(self):
        return self.mEvalSpace

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def getInternalName(self):
        return self.mInternalName

    def getVarDescr(self):
        return self.mVarDescr

    def getPresentationInfo(self):
        return self.mPresentationInfo

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

    def _setScreened(self, value=True):
        self.mScreened = value

    def getMean(self):
        return self.mDescr.get("mean")

    def getDescr(self):
        return self.mDescr

    def getDimName(self):
        return self.mDimName

    def prepareStat(self, stat_ctx, incomplete_mode=False):
        ret_handle = deepcopy(self.mPresentationInfo)
        doc_ref = self.mEvalSpace.getVariableDocRef(self)
        if doc_ref:
            ret_handle["var-doc-ref"] = doc_ref
        if incomplete_mode:
            ret_handle["incomplete"] = True
        return ret_handle

#===============================================
#===============================================
class NumUnitSupport:
    def buildCondition(self, cond_data, eval_h):
        min_val, min_eq, max_val, max_eq = cond_data[2]
        return self.getEvalSpace().makeNumericCond(
            self, min_val, min_eq, max_val, max_eq)

#===============================================
class EnumUnitSupport:
    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]
        if len(variants) == 0:
            if eval_h is not None:
                eval_h.operationError(
                    cond_data, f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()
        return self.getEvalSpace().makeEnumCond(
            self, variants, filter_mode)

    def filterActualVariants(self, variants):
        return sorted(set(variants) & self.getVariantSet().makeValueSet())

    def evalExtraVariants(self, variants):
        return self.getVariantSet().makeValueSet() - set(variants)

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

    def buildCondition(self, cond_data, eval_h, context=None):
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

    def makeInfoStat(self, eval_h, stat_ctx, point_no):
        return VarUnit.prepareStat(self, stat_ctx, None)

    @abc.abstractmethod
    def locateContext(self, cond_data, eval_h):
        return None

    @abc.abstractmethod
    def makeParamStat(self, condition, parameters, eval_h, stat_ctx):
        return None

    @abc.abstractmethod
    def validateArgs(self, func_args):
        assert False, "Abstract func validaton?"

    def buildCondition(self, cond_data, eval_h):
        context = self.locateContext(cond_data, eval_h)
        return ComplexEnumUnit.buildCondition(
            self, cond_data, eval_h, context)

#===============================================
#===============================================
class ReservedNumUnit(NumUnitSupport):
    def __init__(self, eval_space, name, sub_kind="int"):
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

    def getVarDescr(self):
        return {}

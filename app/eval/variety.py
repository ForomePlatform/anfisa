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
from collections import defaultdict, Counter

from forome_tools.variants import VariantSet
from app.config.a_config import AnfisaConfig
from .condition import ConditionMaker
from .var_unit import VarUnit

#===============================================
class MultiStatusUnitAdapter:
    def __init__(self, base_unit_h):
        self.mBaseUnit = base_unit_h
        self.mSeparator = base_unit_h.getDescr()["separator"]
        self.mSingleSet = set()
        self.mMultiMap = defaultdict(list)
        self.mLenCounts = Counter()
        whole_set = set()
        for info in base_unit_h.getDescr()["variants"]:
            val = info[0]
            seq = val.split(self.mSeparator)
            self.mLenCounts[len(seq)] += 1
            if len(seq) == 1:
                self.mSingleSet.add(val)
            else:
                for nm in seq:
                    self.mMultiMap[nm].append(val)
            whole_set |= set(seq)
        self.mVariantSet = VariantSet(sorted(whole_set))
        if base_unit_h.getEvalSpace().getDS().getDSKind() == "ws":
            self.mSingleIdxMap = dict()
            self.mMultiIdxMap = defaultdict(set)
            for idx, info in enumerate(base_unit_h.getDescr()["variants"]):
                val = info[0]
                seq = val.split(self.mSeparator)
                if len(seq) == 1:
                    self.mSingleIdxMap[idx] = self.mVariantSet.indexOf(seq[0])
                else:
                    self.mMultiIdxMap[idx] = self.mVariantSet.makeIdxSet(seq)

    def getBaseUnit(self):
        return self.mBaseUnit

    def getVariantSet(self):
        return self.mVariantSet

    def _logStart(self, ds_name):
        cnt1, cnt2 = len(self.mSingleSet), len(self.mMultiMap)
        counts = self.mLenCounts
        logging.info(f"Variety {ds_name}:{self.getName()} started with:"
            f"\tsingle: {cnt1}, multi: {cnt2} variants, counts={counts}")

    def filterActualVariants(self, variants):
        return sorted(set(variants) & self.mVariantSet.makeValueSet())

    def evalExtraVariants(self, variants):
        return set(self.mVariantSet.makeValueSet()) - set(variants)

    def mapVariants(self, variants):
        ret = set()
        for var in variants:
            if var in self.mSingleSet:
                ret.add(var)
            if var in self.mMultiMap:
                for entry in self.mMultiMap[var]:
                    ret.add(entry)
        return sorted(ret)

    def _makeBaseCond(self, variants, filter_mode):
        base_variants = self.mapVariants(variants)
        ret = self.getEvalSpace().makeEnumCond(
            self.mBaseUnit, base_variants, filter_mode)
        ret.setPreForm(ConditionMaker.condEnum(
            self.getName(), variants, filter_mode))
        return ret

    def _fillRecord(self, inp_data, rec_no):
        self.mBaseUnit.fillRecord(inp_data, rec_no)

    def _collectVariantStat(self, condition, eval_h, panel_seq = None):
        var_cnt = defaultdict(int)
        panel_cnt, panel_res = None, None
        if panel_seq is not None:
            panel_cnt = {pname: 0 for pname, _ in panel_seq}
        base_stat = self.mBaseUnit.makeStat(condition, eval_h, None)
        for base_var, count in base_stat["variants"]:
            if count < 1:
                continue
            names = set(base_var.split(self.mSeparator))
            for nm in names:
                var_cnt[nm] += count
            if panel_seq is not None:
                for pname, pnames in panel_seq:
                    if len(pnames & names) > 0:
                        panel_cnt[pname] += count
        if panel_cnt is not None:
            panel_res = [[pname, panel_cnt[pname]]
                for pname, _ in panel_seq]
        return {var: [var, cnt] for var, cnt in var_cnt.items()}, panel_res

    def getRecVal(self, rec_no):
        # Actual in ws context only
        if rec_no in self.mSingleIdxMap:
            return {self.mSingleIdxMap[rec_no]}
        return self.mMultiIdxMap[rec_no]

#===============================================
class VarietySupport:
    @staticmethod
    def makePanelDescr(descr, sub_kind = None):
        return {
            "name": descr["panel-name"],
            "no": descr["no"],
            "vgroup": descr.get("vgroup"),
            "kind": "enum",
            "mean": "panel",
            "dim-name": "panel." + descr["panel-type"],
            "sub-kind": "multi" if sub_kind is None else sub_kind
        }

    def __init__(self, base_descr, sub_kind = None):
        self.mPanelUnit = VarietyPanelUnit(self,
            VarietySupport.makePanelDescr(base_descr, sub_kind),
            sub_kind)
        self.mPanelType = base_descr["panel-type"]
        self.mPanelKind = "panel." + self.mPanelType
        self.mDefaultRestSize = AnfisaConfig.configOption("max.rest.size")

    def getPanelUnit(self):
        return self.mPanelUnit

    def iterPanels(self):
        return self.getEvalSpace().getDS().iterPanels(self.mPanelType)

    @staticmethod
    def _varSeq(var_dict, names):
        ret = []
        for nm in names:
            if nm not in var_dict:
                ret.append([nm, 0])
            else:
                ret.append(var_dict[nm])
        return ret

    @staticmethod
    def _countSeq(variants):
        return sum(info[1] > 0 for info in variants)

    def _makeStat(self, condition, eval_h, stat_ctx):
        ret_handle = self.prepareStat(stat_ctx)
        base_panel_name = (stat_ctx.get(self.getName() + ".base-panel")
            if stat_ctx is not None else None)
        if base_panel_name:
            base_panel = self.getEvalSpace().getDS().pickSolEntry(
                self.mPanelKind, base_panel_name)
            panel_mode = False
        else:
            base_panel = self.getEvalSpace().getDS().getSpecialSolEntry(
                self.mPanelKind)
            panel_mode = eval_h is not None
        ret_handle["base-panel"] = base_panel.getName()
        max_rest_size = (stat_ctx.get("max-rest-size", self.mDefaultRestSize)
            if stat_ctx is not None else self.mDefaultRestSize)

        if panel_mode:
            panel_seq = [[pname, set(names)]
                for pname, names in self.iterPanels()]
        else:
            panel_seq = None

        var_dict, panel_res = self._collectVariantStat(
            condition, eval_h, panel_seq)

        if eval_h is None:
            ret_handle["variants"] = self._varSeq(
                var_dict, iter(self.mVariantSet))
            return ret_handle

        total_cnt = self._countSeq(var_dict.values())
        res_variants = self._varSeq(var_dict, base_panel.getSymList())
        split_info = [["active", len(res_variants)]]
        base_names = set(base_panel.getSymList())
        base_cnt = self._countSeq(res_variants)
        rest_cnt = total_cnt - base_cnt
        if total_cnt < max_rest_size:
            if rest_cnt > 0:
                split_info.append(["rest", rest_cnt])
                for nm in sorted(var_dict.keys()):
                    if nm in base_names:
                        continue
                    info = var_dict[nm]
                    if info[1] > 0:
                        res_variants.append(info)
        else:
            used_names = self.getEvalSpace().getUsedDimValues(
                eval_h, self.getDimName()) - base_names
            if len(used_names) > 0:
                split_info.append(["used", len(used_names)])
                res_variants += self._varSeq(var_dict, sorted(used_names))
            ret_handle["rest-count"] = total_cnt - self._countSeq(res_variants)
        ret_handle["variants"] = res_variants
        ret_handle["split-info"] = split_info

        if panel_res is not None:
            ret_handle["panels"] = panel_res
            ret_handle["panel-state"] = self.getEvalSpace().getDS().getSolEnv(
                ).getIntVersion(self.mPanelKind)
        if self.isDetailed():
            ret_handle["detailed"] = True
        return ret_handle

#===============================================
class VarietyUnit(VarUnit, MultiStatusUnitAdapter, VarietySupport):
    @staticmethod
    def makeVarietyDescr(descr):
        return {
            "name": descr["variety-name"],
            "no": descr["no"],
            "vgroup": descr.get("vgroup"),
            "kind": "enum",
            "sub-kind": "multi",
            "dim-name": descr["panel-type"]
        }

    def __init__(self, base_unit_h):
        VarUnit.__init__(self, base_unit_h.getEvalSpace(),
            self.makeVarietyDescr(
            base_unit_h.getDescr()), "enum")
        MultiStatusUnitAdapter.__init__(self, base_unit_h)
        VarietySupport.__init__(self, base_unit_h.getDescr())
        self.getInfo()["panel-name"] = self.getPanelUnit().getName()
        self._logStart(self.getEvalSpace().getDS().getName())

    def makeBaseCond(self, variants, filter_mode):
        return self._makeBaseCond(variants, filter_mode)

    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]
        if len(variants) == 0:
            eval_h.operationError(cond_data,
                f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()
        return self._makeBaseCond(variants, filter_mode)

    def fillRecord(self, inp_data, rec_no):
        self._fillRecord(inp_data, rec_no)

    def makeStat(self, condition, eval_h, stat_ctx):
        return self._makeStat(condition, eval_h, stat_ctx)

#===============================================
class VarietyPanelUnit(VarUnit):

    def __init__(self, variety_h, descr, sub_kind = None):
        VarUnit.__init__(self, variety_h.getEvalSpace(),
            descr, "enum", "multi" if sub_kind is None else sub_kind)
        self.mVariety = variety_h
        self.getInfo()["variety-name"] = self.mVariety.getName()

    def getVariety(self):
        return self.mVariety

    def mapVariants(self, variants):
        collected = set()
        for pname, names in self.mVariety.iterPanels():
            if pname in variants:
                collected |= set(names)
        return self.mVariety.mapVariants(collected)

    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]

        if len(variants) == 0:
            eval_h.operationError(cond_data,
                f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()

        if filter_mode == "AND" and len(variants) > 1:
            cond_seq = []
            for pname in variants:
                svariants = self.mapVariants([pname])
                if len(svariants) == 0:
                    cond_seq = None
                    break
                cond_seq.append(self.mVariety.makeBaseCond(
                    svariants, "OR"))
            if cond_seq is not None:
                cond_res = self.getEvalSpace().joinAnd(cond_seq)
            else:
                cond_res = self.getEvalSpace().getCondNone()
        else:
            svariants = self.mapVariants(variants)
            if len(svariants) > 0:
                cond_res = self.mVariety.makeBaseCond(
                    svariants, filter_mode)
            else:
                cond_res = self.getEvalSpace().getCondNone()
        cond_res.setPreForm(ConditionMaker.condEnum(
            self.getName(), variants, filter_mode))
        return cond_res

    def fillRecord(self, inp_data, rec_no):
        pass

    def makeStat(self, condition, eval_h, stat_ctx):
        ret_handle = self.prepareStat(stat_ctx)
        ret_handle["variants"] = []
        if self.mVariety.isDetailed():
            ret_handle["detailed"] = True
        return ret_handle

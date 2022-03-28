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

from .var_unit import VarUnit
#===============================================
class VarietyUnit(VarUnit):
    @staticmethod
    def makeDescr(descr, key_val):
        return {
            "name": descr[key_val],
            "no": descr["no"],
            "vgroup": descr.get("vgroup"),
            "kind": "enum",
            "sub-kind": "multi"
        }

    def __init__(self, base_unit_h, full_mode):
        VarUnit.__init__(self, base_unit_h.getEvalSpace(),
            self.makeDescr(base_unit_h.getDescr(), "atom-name"),
            "enum", "multi")
        self.mBaseUnit = base_unit_h
        self.mFullMode = full_mode
        self.mPanelUnit = VarietyPanelUnit(self,
            self.makeDescr(base_unit_h.getDescr(), "panel-name"))
        self.mSeparator = base_unit_h.getDescr()["separator"]
        self.mPanelType = base_unit_h.getDescr()["panel-type"]
        self.getInfo()["panel-name"] = self.mPanelUnit.getName()
        self.mSingleSet = set()
        self.mMultiMap = defaultdict(list)
        self.mAllAtoms = set()
        counts = Counter()
        for info in base_unit_h.getDescr()["variants"]:
            val = info[0]
            seq = val.split(self.mSeparator)
            counts[len(seq)] += 1
            if len(seq) == 1:
                self.mSingleSet.add(val)
            else:
                for nm in seq:
                    self.mMultiMap[nm].append(val)
            self.mAllAtoms |= set(seq)
        ds_name = self.getEvalSpace().getDS().getName()
        cnt1, cnt2 = len(self.mSingleSet), len(self.mMultiMap)
        logging.info(f"Variety {ds_name}:{self.getName()} started with:"
            f"\tsingle: {cnt1}, multi: {cnt2} atoms, counts={counts}")

    def getPanelUnit(self):
        return self.mPanelUnit

    def getPanelType(self):
        return self.mPanelType

    def mapVariants(self, variants):
        ret = set()
        for var in variants:
            if var in self.mSingleSet:
                ret.add(var)
            if var in self.mMultiMap:
                for entry in self.mMultiMap[var]:
                    ret.add(entry)
        return sorted(ret)

    def makeBaseCond(self, variants, filter_mode):
        base_variants = self.mapVariants(variants)
        return self.getEvalSpace().makeEnumCond(
            self.mBaseUnit, base_variants, filter_mode)

    def iterPanels(self):
        return (self.getEvalSpace().
            getDS().iterPanels(self.mPanelType))

    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]
        if len(variants) == 0:
            eval_h.operationError(cond_data,
                f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()
        return self.makeBaseCond(variants, filter_mode)

    def fillRecord(self, inp_data, rec_no):
        self.mBaseUnit.fillRecord(inp_data, rec_no)

    def makeStat(self, condition, eval_h, stat_ctx):
        base_stat = self.mBaseUnit.makeStat(condition, eval_h, None)

        if self.mFullMode:
            free_names = self.mAllAtoms
        else:
            free_names = set()
            key_ctx = "free." + self.getName()
            if stat_ctx is not None and key_ctx in stat_ctx:
                free_names = set(stat_ctx[key_ctx])

        atom_names = free_names.copy()
        panel_names = dict()
        panel_cnt = dict()
        for pname, names in self.iterPanels():
            names = set(names)
            panel_names[pname] = names
            panel_cnt[pname] = 0
            if not self.mFullMode:
                atom_names |= names
        atom_cnt = {nm: 0 for nm in atom_names}

        for base_var, count in base_stat["variants"]:
            if count < 1:
                continue
            names = set(base_var.split(self.mSeparator))
            if not self.mFullMode:
                names &= atom_names
            if len(names) == 0:
                continue
            for nm in names:
                atom_cnt[nm] += 1
            for pname, pnames in panel_names.items():
                if len(pnames & names) > 0:
                    panel_cnt[pname] += 1

        ret_handle = self.prepareStat(stat_ctx)
        if not self.mFullMode:
            ret_handle["free-atoms"] = sorted(free_names)
        ret_handle["panel-atoms"] = [[pname, sorted(panel_names[pname])]
            for pname in sorted(panel_cnt.keys())]
        ret_handle["variants"] = [[nm, atom_cnt[nm]]
            for nm in sorted(atom_cnt.keys())]
        ret_handle["panels"] = [[pname, panel_cnt[pname]]
            for pname in sorted(panel_cnt.keys())]
        return ret_handle

#===============================================
class VarietyPanelUnit(VarUnit):

    def __init__(self, variety_h, descr):
        VarUnit.__init__(self, variety_h.getEvalSpace(),
            descr, "enum", "multi")
        self.mVariety = variety_h
        self.getInfo()["atom-name"] = self.mVariety.getName()

    def mapVariants(self, variants):
        collected = set()
        for pname, names in self.mVariety.iterPanels():
            collected |= set(names)
        return self.mVariety.mapVariants(collected)

    def buildCondition(self, cond_data, eval_h):
        filter_mode, variants = cond_data[2:]

        if len(variants) == 0:
            eval_h.operationError(cond_data,
                f"Enum {self.getName}: empty set of variants")
            return self.getEvalSpace().getCondNone()

        return self.mVariety.makeBaseCond(
            self.mapVariants(variants), filter_mode)

    def fillRecord(self, inp_data, rec_no):
        pass

    def makeStat(self, condition, eval_h, stat_ctx):
        ret_handle = self.prepareStat(stat_ctx)
        ret_handle["variants"] = []
        return ret_handle

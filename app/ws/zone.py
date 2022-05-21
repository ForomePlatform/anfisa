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

#===============================================
class ZoneH:
    def __init__(self, ds_h, title):
        self.mDS = ds_h
        self.mTitle = title

    def _setTitle(self, title):
        self.mTitle = title

    def getDS(self):
        return self.mDS

    def getTitle(self):
        return self.mTitle

    def makeValuesReport(self, serial_mode = False):
        ret = {
            "zone": self.getName(),
            "title": self.getTitle()}
        if not serial_mode:
            ret["variants"] = self.getVariantList()
        return ret

#===============================================
class FilterZoneH(ZoneH):
    def __init__(self, ds_h, title, unit):
        ZoneH.__init__(self, ds_h, title)
        self.mUnit = unit

    def getName(self):
        return self.mUnit.getName()

    def getVariantList(self):
        return list(iter(self.mUnit.getVariantSet()))

    def getRestrictF(self, variants):
        cond = self.getDS().getEvalSpace().makeEnumCond(
            self.mUnit, variants)
        return lambda rec_no: cond.recInSelection(rec_no)

#===============================================
class PanelZoneH(ZoneH):
    def __init__(self, ds_h, title, unit_h):
        ZoneH.__init__(self, ds_h, title)
        self.mPanelUnit = unit_h
        self.mVarietyUnit = unit_h.getVariety()

    def getName(self):
        return self.mPanelUnit.getName()

    def getVariantList(self):
        return list(pname
            for pname, _ in self.mVarietyUnit.iterPanels())

    def inVariants(self, rec_no, variants):
        v_idx_set = self.mVarietyUnit.getRecVal(rec_no)
        rec_names = self.mVarietyUnit.getVariantSet().makeValueSet(v_idx_set)
        for pname, names in self.mVarietyUnit.iterPanels():
            if pname in variants and len(rec_names & set(names)) > 0:
                return True
        return False

    def getRestrictF(self, variants):
        return lambda rec_no: self.inVariants(rec_no, variants)

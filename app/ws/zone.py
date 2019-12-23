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
    def __init__(self, workspace, title):
        self.mDS = workspace
        self.mTitle = title

    def _setTitle(self, title):
        self.mTitle = title

    def getDS(self):
        return self.mDS

    def getTitle(self):
        return self.mTitle

    def makeValuesReport(self):
        return {
            "zone": self.getName(),
            "title": self.getTitle(),
            "variants": self.getVariants()}

#===============================================
class FilterZoneH(ZoneH):
    def __init__(self, workspace, title, unit):
        ZoneH.__init__(self, workspace, title)
        self.mUnit = unit

    def getName(self):
        return self.mUnit.getName()

    def getVariants(self):
        return self.mUnit.getVariantList()

    def getRestrictF(self, variants):
        cond = self.getDS().getEvalSpace().makeEnumCond(
            self.mUnit, variants)
        return lambda rec_no: cond.recInSelection(rec_no)

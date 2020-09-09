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

from forome_tools.variants import VariantSet
from app.config.a_config import AnfisaConfig
from app.eval.var_unit import ComplexEnumUnit
#===============================================
class RulesUnit(ComplexEnumUnit):
    sSetupData = AnfisaConfig.configOption("rules.setup")

    def __init__(self, ds_h):
        ComplexEnumUnit.__init__(self, ds_h.getEvalSpace(), {
            "name": self.sSetupData["name"],
            "sub-kind": "multi",
            "title": self.sSetupData["title"],
            "vgroup": self.sSetupData["vgroup"],
            "render": self.sSetupData["render"]}, "enum")
        self.mDS = ds_h

    def isInDTrees(self):
        return False

    def isDetailed(self):
        return True

    def isScreened(self):
        return self.mDS.noSolEntries("dtree")

    def getVariantSet(self):
        return VariantSet([dtree_h.getDTreeName()
            for dtree_h in self.mDS.iterSolEntries("dtree")])

    def iterComplexCriteria(self, context, variants = None):
        for dtree_h in self.mDS.iterSolEntries("dtree"):
            if variants is not None and dtree_h.getDTreeName() not in variants:
                continue
            dtree_h.activate()
            yield dtree_h.getDTreeName(), dtree_h.getFinalCondition()

    def makeStat(self, condition, eval_h):
        ret_handle = self.prepareStat()
        self.collectComplexStat(ret_handle, condition,
            detailed = self.isDetailed())
        return ret_handle

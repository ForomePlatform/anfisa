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

from utils.variants import VariantSet
from app.config.a_config import AnfisaConfig
from app.filter.unit import Unit, ComplexEnumSupport
from app.filter.condition import validateEnumCondition
#===============================================
class RulesUnit(Unit, ComplexEnumSupport):
    sSetupData = AnfisaConfig.configOption("rules.setup")

    def __init__(self, ds_h, ):
        Unit.__init__(self, {
            "kind": "enum",
            "name": self.sSetupData["name"],
            "title": self.sSetupData["title"],
            "vgroup": self.sSetupData["vgroup"],
            "render": self.sSetupData["render"]})
        self.mDS = ds_h
        self.getCondEnv().addEnumUnit(self)

    def getDS(self):
        return self.mDS

    def getCondEnv(self):
        return self.mDS.getCondEnv()

    def getVariantSet(self):
        return VariantSet([dtree_h.getDTreeName()
            for dtree_h in self.mDS.iterSolEntries("dtree")])

    def isDetailed(self):
        for dtree_h in self.mDS.iterSolEntries("dtree"):
            dtree_h.activate()
            if dtree_h.getFinalCondition().isDetailed():
                return True
        return False

    def iterComplexCriteria(self, context, variants = None):
        for dtree_h in self.mDS.iterSolEntries("dtree"):
            dtree_h.activate()
            yield dtree_h.getDTreeName(), dtree_h.getFinalCondition()

    def validateCondition(self, cond_data):
        return validateEnumCondition(cond_data)

    def parseCondition(self, cond_data):
        return self.makeComplexCondition(
            cond_data[2], cond_data[3])

    def fillRecord(self, inp_data, rec_no):
        pass

    def makeStat(self, condition, repr_context = None):
        ret = self.prepareStat()
        detailed = self.isDetailed()
        ret.append(self.collectComplexStat(self.mDS, condition,
            detailed = detailed))
        return ret


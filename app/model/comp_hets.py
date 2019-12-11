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

from app.config.a_config import AnfisaConfig
from app.filter.unit import Unit, ComplexEnumSupport
from app.filter.condition import validateEnumCondition

#=====================================
class CompHetsOperativeUnit(Unit, ComplexEnumSupport):
    sSetupData = AnfisaConfig.configOption("comp-hets.setup")

    @classmethod
    def setupCondEnv(cls, ds_h):
        cond_env = ds_h.getCondEnv()
        if not ds_h.testRequirements({"trio"}):
            return False
        for var_info in cls.sSetupData[
                "op-variables." + cond_env.getCondKind()]:
            name, gene_unit = var_info[:2]
            title = var_info[2] if len(var_info) > 2 else name
            cond_env.addOperativeUnit(
                CompHetsOperativeUnit(ds_h, name, gene_unit, title))
        return True

    def __init__(self, ds_h, name, gene_unit, title):
        Unit.__init__(self, {
            "name": name,
            "title": title,
            "kind": "enum",
            "vgroup": self.sSetupData["vgroup"],
            "render": "operative"})
        self.mDS = ds_h
        self.mCondEnv = self.mDS.getCondEnv()
        self.mZygUnit = self.mDS.getUnit(self.sSetupData["zygosity.unit"])
        self.mGeneUnit = self.mDS.getUnit(gene_unit)

    def getDS(self):
        return self.mDS

    def getCondEnv(self):
        return self.mDS.getCondEnv()

    def _prepareZygConditions(self, trio_info):
        zyg_base, zyg_father, zyg_mother = [
            self.mZygUnit.getFamUnit(idx) for idx in trio_info[1:]]
        return [self.mCondEnv.makeNumericCond(zyg_base, [1, 1]),
            self.mCondEnv.joinAnd([
                self.mCondEnv.makeNumericCond(zyg_father, [1, 1]),
                self.mCondEnv.makeNumericCond(zyg_mother, [0, 0])]),
            self.mCondEnv.joinAnd([
                self.mCondEnv.makeNumericCond(zyg_mother, [1, 1]),
                self.mCondEnv.makeNumericCond(zyg_father, [0, 0])])]

    def prepareImport(self, actual_condition):
        ret = dict()
        for trio_info in self.mDS.getFamilyInfo().getTrioSeq():
            self._prepareTrio(trio_info, actual_condition, ret)
        return ret

    def _prepareTrio(self, trio_info, actual_condition, ret):
        logging.info("Comp-hets eval for %s" % trio_info[0])
        c_proband, c_father, c_mother = self._prepareZygConditions(trio_info)

        genes1 = set()
        stat_info = self.mGeneUnit.makeStat(self.mCondEnv.joinAnd(
            [actual_condition, c_proband, c_father]))
        for info in stat_info[2]:
            gene, count = info[:2]
            if count > 0:
                genes1.add(gene)
        logging.info("Eval genes1 for %s comp-hets: %d" %
            (trio_info[0], len(genes1)))
        if len(genes1) is None:
            return
        genes2 = set()
        stat_info = self.mGeneUnit.makeStat(self.mCondEnv.joinAnd(
            [actual_condition, c_proband, c_mother]))
        for info in stat_info[2]:
            gene, count = info[:2]
            if count > 0:
                genes2.add(gene)
        logging.info("Eval genes2 for %s comp-hets: %d" %
            (trio_info[0], len(genes2)))
        actual_genes = genes1 & genes2
        logging.info("Result genes for comp-hets: %d" % len(actual_genes))
        if len(actual_genes) == 0:
            return
        ret[trio_info[0]] = sorted(actual_genes)

    def iterComplexCriteria(self, context, variants = None):
        for trio_info in self.mDS.getFamilyInfo().getTrioSeq():
            if variants is not None and trio_info[0] not in variants:
                continue
            gene_seq = context["comp"].get(trio_info[0])
            if not gene_seq:
                continue
            c_proband, c_father, c_mother = self._prepareZygConditions(
                trio_info)
            yield trio_info[0], self.mCondEnv.joinAnd([
                c_proband, c_father.addOr(c_mother),
                self.mCondEnv.makeEnumCond(self.mGeneUnit, gene_seq)])

    def makeActiveStat(self, condition, flt_base_h, repr_context):
        ret = self.prepareStat()
        if self.mGeneUnit.isDetailed():
            ret[1]["detailed"] = True
        ret.append(self.collectComplexStat(self.mDS, condition,
            {"comp": flt_base_h.getCompData(self.getName())},
            detailed = self.mGeneUnit.isDetailed()))
        return ret

    def validateCondition(self, cond_data):
        return validateEnumCondition(cond_data)

    def parseCondition(self, cond_data, calc_data):
        return self.makeComplexCondition(
            cond_data[2], cond_data[3], {"comp": calc_data})

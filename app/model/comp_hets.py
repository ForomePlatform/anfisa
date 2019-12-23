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

from app.eval.var_unit import ComplexEnumUnit
from app.eval.operative import OperativeUnit

#=====================================
class CompHetsUnit(ComplexEnumUnit):
    @staticmethod
    def makeIt(ds_h, descr, gene_unit, before = None, after = None):
        unit_h = CompHetsUnit(ds_h, descr, gene_unit)
        op_unit_h = OperativeUnit(unit_h)
        ds_h.getEvalSpace()._insertUnit(
            op_unit_h, before = before, after = after)

    def __init__(self, ds_h, descr, gene_unit):
        ComplexEnumUnit.__init__(self, ds_h.getEvalSpace(), descr, "enum")
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mGeneUnit = self.getEvalSpace().getUnit(gene_unit)

    def _prepareZygConditions(self, trio_info):
        eval_space = self.getEvalSpace()
        zyg_base, zyg_father, zyg_mother = [
            eval_space.getZygUnit(idx) for idx in trio_info[1:]]
        return [eval_space.makeNumericCond(zyg_base, zyg_bounds = "1"),
            eval_space.joinAnd([
                eval_space.makeNumericCond(zyg_father, zyg_bounds = "1"),
                eval_space.makeNumericCond(zyg_mother, zyg_bounds = "0")]),
            eval_space.joinAnd([
                eval_space.makeNumericCond(zyg_mother, zyg_bounds = "1"),
                eval_space.makeNumericCond(zyg_father, zyg_bounds = "0")])]

    def prepareImport(self, actual_condition):
        ret = dict()
        for trio_info in self.mFamilyInfo.getTrioSeq():
            self._prepareTrio(trio_info, actual_condition, ret)
        return ret

    def _prepareTrio(self, trio_info, actual_condition, ret):
        logging.info("Comp-hets eval for %s" % trio_info[0])
        c_proband, c_father, c_mother = self._prepareZygConditions(trio_info)

        genes1 = set()
        stat_info = self.mGeneUnit.makeStat(self.getEvalSpace().joinAnd(
            [actual_condition, c_proband, c_father]), repr_context = None)
        for info in stat_info["variants"]:
            gene, count = info[:2]
            if count > 0:
                genes1.add(gene)
        logging.info("Eval genes1 for %s comp-hets: %d" %
            (trio_info[0], len(genes1)))
        if len(genes1) is None:
            return
        genes2 = set()
        stat_info = self.mGeneUnit.makeStat(self.getEvalSpace().joinAnd(
            [actual_condition, c_proband, c_mother]), repr_context = None)
        for info in stat_info["variants"]:
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
        for trio_info in self.mFamilyInfo.getTrioSeq():
            if variants is not None and trio_info[0] not in variants:
                continue
            gene_seq = context.get(trio_info[0])
            if not gene_seq:
                continue
            c_proband, c_father, c_mother = self._prepareZygConditions(
                trio_info)
            yield trio_info[0], self.getEvalSpace().joinAnd([
                c_proband, c_father.addOr(c_mother),
                self.getEvalSpace().makeEnumCond(self.mGeneUnit, gene_seq)])

    def locateContext(self, cond_data, eval_h):
        hash_code, actual_condition = eval_h.getImportSupport(self.getName())
        context = eval_h.getEvalSpace().getOpCacheValue(
            self.getName(), hash_code)
        if context is None:
            context = self.prepareImport(actual_condition)
            eval_h.getEvalSpace().setOpCacheValue(
                self.getName(), hash_code, context)
        return context

    def makeStat(self, condition, repr_context):
        ret_handle = self.prepareStat()
        self.collectComplexStat(ret_handle, condition,
            self.locateContext(None, repr_context["eval"]),
            detailed = self.mGeneUnit.isDetailed())
        return ret_handle

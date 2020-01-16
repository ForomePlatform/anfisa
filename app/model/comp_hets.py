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
from cachetools import LRUCache

from app.config.a_config import AnfisaConfig
from app.eval.var_unit import FunctionUnit
#=====================================
class CompHetsUnit(FunctionUnit):
    sMaxGeneCompCount = AnfisaConfig.configOption("max.gene.comp.count")

    @staticmethod
    def makeIt(ds_h, descr, gene_levels, before = None, after = None):
        unit_h = CompHetsUnit(ds_h, descr, gene_levels)
        ds_h.getEvalSpace()._insertUnit(
            unit_h, before = before, after = after)

    def __init__(self, ds_h, descr, gene_levels):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "comp-hets", parameters = ["approx", "state"])
        self.mFamilyInfo = ds_h.getFamilyInfo()
        self.mGeneLevelIdxs = dict()
        self.mGeneUnits = dict()
        self.mApproxInfo = []
        for key, unit_name, level_title in gene_levels:
            self.mGeneLevelIdxs[key] = len(self.mGeneUnits)
            self.mGeneUnits[key] = self.getEvalSpace().getUnit(unit_name)
            assert self.mGeneUnits[key] is not None, (
                "Bad gene unit: " + unit_name)
            self.mApproxInfo.append([key, level_title])
        self.mTrioNames = [trio_info[0]
            for trio_info in self.mFamilyInfo.getTrioSeq()]
        self.mOpCache = LRUCache(
            AnfisaConfig.configOption("comp-hets.cache.size"))

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

    def buildConditions(self, gene_unit, actual_condition):
        ret_handle = dict()
        for trio_info in self.mFamilyInfo.getTrioSeq():
            self._buildTrioCond(trio_info,
                gene_unit, actual_condition, ret_handle)
        return ret_handle

    def _buildTrioCond(self, trio_info,
            gene_unit, actual_condition, ret_handle):
        logging.info("Comp-hets eval for %s / %s" %
            (trio_info[0], gene_unit.getName()))
        c_proband, c_father, c_mother = self._prepareZygConditions(trio_info)

        genes1 = set()
        stat_info = gene_unit.makeStat(self.getEvalSpace().joinAnd(
            [actual_condition, c_proband, c_father]), eval_h = None)
        for info in stat_info["variants"]:
            gene, count = info[:2]
            if count > 0:
                genes1.add(gene)
        logging.info("Eval genes1 for %s comp-hets: %d" %
            (trio_info[0], len(genes1)))
        if len(genes1) is None:
            return
        genes2 = set()
        stat_info = gene_unit.makeStat(self.getEvalSpace().joinAnd(
            [actual_condition, c_proband, c_mother]), eval_h = None)
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
        if len(actual_genes) >= self.sMaxGeneCompCount:
            logging.info("Heavy condition")
            ret_handle[trio_info[0]] = None
        else:
            ret_handle[trio_info[0]] = sorted(actual_genes)

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        gene_unit = self.mGeneUnits[context["approx"]]
        for trio_info in self.mFamilyInfo.getTrioSeq():
            if variants is not None and trio_info[0] not in variants:
                continue
            gene_seq = context["trio"].get(trio_info[0])
            if not gene_seq:
                yield trio_info[0], self.getEvalSpace().getCondNone()
                continue
            c_proband, c_father, c_mother = self._prepareZygConditions(
                trio_info)
            yield trio_info[0], self.getEvalSpace().joinAnd([
                c_proband, c_father.addOr(c_mother),
                self.getEvalSpace().makeEnumCond(gene_unit, gene_seq)])

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["trio-variants"] = self.mTrioNames
        ret_handle["approx-modes"] = self.mApproxInfo
        ret_handle["labels"] = eval_h.getLabelPoints(point_no)
        return ret_handle

    def _locateContext(self, parameters, eval_h, point_no = None):
        if "state" in parameters:
            actual_condition = eval_h.getLabelCondition(
                parameters["state"], point_no)
            if actual_condition is None:
                return None, ("State label %s not defined"
                    % parameters["state"])
        else:
            actual_condition = eval_h.getActualCondition(point_no)
        approx_mode = parameters.get("approx", self.mApproxInfo[0][0])
        if approx_mode not in self.mGeneUnits:
            return None, "Improper approx mode %s" % approx_mode
        build_id = approx_mode + '|' + actual_condition.hashCode()
        with self.getEvalSpace().getDS():
            context = self.mOpCache.get(build_id)
        if context is None:
            context = {
                "approx": approx_mode,
                "trio": self.buildConditions(self.mGeneUnits[approx_mode],
                    actual_condition)}
            with self.getEvalSpace().getDS():
                self.mOpCache[build_id] = context
        if None in context["trio"].values():
            context, "Too heavy condition"
        return context, None

    def locateContext(self, cond_data, eval_h):
        point_no, _ = eval_h.locateCondData(cond_data)
        context, err_msg = self._locateContext(cond_data[4], eval_h, point_no)
        if err_msg:
            eval_h.operationError(cond_data, err_msg)
        return context

    def validateArgs(self, parameters):
        if ("state" in parameters
                and not isinstance(parameters["state"], str)):
            return "Bad state parameter"
        if ("approx" in parameters
                and not isinstance(parameters["approx"], str)):
            return "Bad approx parameter"
        return None

    def makeParamStat(self, condition, parameters, eval_h, point_no):
        context, err_msg = self._locateContext(parameters, eval_h, point_no)
        ret_handle = self.prepareStat()
        self.collectComplexStat(ret_handle, condition, context,
            self.mGeneUnits[context["approx"]].isDetailed())
        if err_msg:
            ret_handle["err"] = err_msg
        return ret_handle

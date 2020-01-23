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
import json
from cachetools import LRUCache
from hashlib import md5

from app.config.a_config import AnfisaConfig
from app.eval.var_unit import FunctionUnit
#=====================================
class CompHetsUnit(FunctionUnit):
    @staticmethod
    def makeIt(ds_h, descr, before = None, after = None):
        unit_h = CompHetsUnit(ds_h, descr)
        ds_h.getEvalSpace()._insertUnit(
            unit_h, before = before, after = after)

    def __init__(self, ds_h, descr):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "comp-hets", parameters = ["approx", "state"])
        self.mZygSupport = ds_h.getZygositySupport()
        self.mOpCache = LRUCache(
            AnfisaConfig.configOption("comp-hets.cache.size"))

    def _buildTrioRequest(self, trio_info,  approx_mode,  actual_condition):
        id_base,  id_father,  id_mother = trio_info[1:]
        c_rq = [
            [1,  {"1": [id_base,  id_father],  "0": [id_mother]}],
            [1,  {"1": [id_base,  id_mother],  "0": [id_father]}]]
        return self.mZygSupport.makeCompoundRequest(
            approx_mode, actual_condition, c_rq, self.getName())

    def buildConditions(self, approx_mode, actual_condition):
        ret_handle = dict()
        for trio_info in self.mZygSupport.getTrioSeq():
            ret_handle[trio_info[0]] = self._buildTrioRequest(
                trio_info, approx_mode, actual_condition)
        return ret_handle

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        trio_dict = context["trio-dict"]
        for trio_id, _, _, _ in self.mZygSupport.getTrioSeq():
            if variants is not None and trio_id not in variants:
                continue
            trio_crit = trio_dict[trio_id]
            if trio_crit is not None:
                yield trio_id,  trio_crit

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["trio-variants"] = [trio_info[0]
            for trio_info in self.mZygSupport.getTrioSeq()]
        ret_handle["approx-modes"] = self.mZygSupport.getApproxInfo()
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
        approx_mode = self.mZygSupport.normalizeApprox(
            parameters.get("approx"))
        if approx_mode is False:
            return None, "Improper approx mode %s" % parameters["approx"]

        build_id = approx_mode + '|' + actual_condition.hashCode()
        with self.getEvalSpace().getDS():
            context = self.mOpCache.get(build_id)
        if context is None:
            context = {
                "approx": approx_mode,
                "trio-dict": self.buildConditions(
                    approx_mode, actual_condition)}
            with self.getEvalSpace().getDS():
                self.mOpCache[build_id] = context
        if None in context["trio-dict"].values():
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
            self.mZygSupport.getGeneUnit(context["approx"]).isDetailed())
        ret_handle.update(parameters)
        if err_msg:
            ret_handle["err"] = err_msg
        return ret_handle

#=====================================
class CompoundRequestUnit(FunctionUnit):
    @staticmethod
    def makeIt(ds_h, descr, before = None, after = None):
        unit_h = CompoundRequestUnit(ds_h, descr)
        ds_h.getEvalSpace()._insertUnit(
            unit_h, before = before, after = after)

    def __init__(self, ds_h, descr):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "comp-request",
            parameters = ["request", "approx", "state"])
        self.mZygSupport = ds_h.getZygositySupport()
        self.mOpCache = LRUCache(
            AnfisaConfig.configOption("comp-hets.cache.size"))

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        yield "True", context["crit"]

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["approx-modes"] = self.mZygSupport.getApproxInfo()
        ret_handle["labels"] = eval_h.getLabelPoints(point_no)
        ret_handle["family"] = self.mZygSupport.getIds()
        ret_handle["affected"] = self.mZygSupport.getAffectedGroup()
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
        approx_mode = self.mZygSupport.normalizeApprox(
            parameters.get("approx"))
        if approx_mode is False:
            return None, "Improper approx mode %s" % parameters["approx"]

        c_rq = parameters.get("request")
        if self.mZygSupport.emptyRequest(c_rq):
            return None, "Empty request"

        build_id = md5(bytes(json.dumps(c_rq, sort_keys = True)
            + approx_mode + '|' + actual_condition.hashCode(),
            encoding="utf-8"))
        with self.getEvalSpace().getDS():
            context = self.mOpCache.get(build_id)
        if context is None:
            context = {
                "approx": approx_mode,
                "crit": self.mZygSupport.makeCompoundRequest(
                    approx_mode, actual_condition, c_rq, self.getName())}
            with self.getEvalSpace().getDS():
                self.mOpCache[build_id] = context
        if context["crit"] is None:
            context, "Too heavy condition"
        return context, None

    def locateContext(self, cond_data, eval_h):
        point_no, _ = eval_h.locateCondData(cond_data)
        context, err_msg = self._locateContext(cond_data[4], eval_h, point_no)
        if err_msg:
            eval_h.operationError(cond_data, err_msg)
        return context

    def validateArgs(self, parameters):
        if "request" not in parameters:
            return "Argument request is required"
        return self.mZygSupport.validateRequest(parameters["request"])

    def makeParamStat(self, condition, parameters, eval_h, point_no):
        context, err_msg = self._locateContext(parameters, eval_h, point_no)
        ret_handle = self.prepareStat()
        self.collectComplexStat(ret_handle, condition, context,
            self.mZygSupport.getGeneUnit(context["approx"]).isDetailed())
        ret_handle.update(parameters)
        if err_msg:
            ret_handle["err"] = err_msg
        return ret_handle

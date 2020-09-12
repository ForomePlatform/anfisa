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

from app.config.a_config import AnfisaConfig
from app.eval.var_unit import FunctionUnit

#===============================================
class InheritanceUnit(FunctionUnit):
    sCaseKeys   = ("homo_recess", "x_linked", "dominant", "compens")
    sCaseLabels = [AnfisaConfig.configOption("zygosity.cases")[key]
        for key in sCaseKeys]

    @staticmethod
    def makeIt(ds_h, descr, before = None, after = None):
        unit_h = InheritanceUnit(ds_h, descr)
        ds_h.getEvalSpace()._insertUnit(unit_h, before = before, after = after)

    def __init__(self, ds_h, descr):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "inheritance-z", parameters = ["problem_group"])
        assert ds_h.testRequirements({"ZYG"})
        self.mZygSupport = ds_h.getZygositySupport()
        self.mAvailLabels = self.sCaseLabels[:]
        if not self.mZygSupport.hasXLinked():
            self.mAvailLabels.remove(
                AnfisaConfig.configOption("zygosity.cases")["x_linked"])

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        p_group = context["p_group"]
        if variants is None or self.sCaseLabels[0] in variants:
            yield (self.sCaseLabels[0],
                self.mZygSupport.conditionZHomoRecess(p_group))
        if variants is None or self.sCaseLabels[1] in variants:
            yield (self.sCaseLabels[1],
                self.mZygSupport.conditionZXLinked(p_group))
        if variants is None or self.sCaseLabels[2] in variants:
            yield (self.sCaseLabels[2],
                self.mZygSupport.conditionZDominant(p_group))
        if variants is None or self.sCaseLabels[3] in variants:
            yield (self.sCaseLabels[3],
                self.mZygSupport.conditionZCompens(p_group))

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["family"] = self.mZygSupport.getNames()
        ret_handle["affected"] = self.mZygSupport.getAffectedGroup()
        ret_handle["available"] = self.mAvailLabels
        return ret_handle

    def makeParamStat(self, condition, parameters, eval_h, point_no):
        ret_handle = self.prepareStat()
        if parameters is None or parameters.get("problem_group") is None:
            p_group = self.mZygSupport.getAffectedGroup()
        else:
            p_group = self.mZygSupport.filter(parameters["problem_group"])
        ret_handle["problem_group"] = sorted(p_group)
        if len(p_group) > 0:
            self.collectComplexStat(ret_handle, condition,
                {"p_group": p_group})
        else:
            ret_handle["variants"] = None
            ret_handle["err"] = "Problem group is empty"
        return ret_handle

    def locateContext(self, cond_data, eval_h):
        p_group = cond_data[4].get("problem_group")
        if p_group is None:
            p_group = self.mZygSupport.getAffectedGroup()
        else:
            extra_names = (set(p_group) - set(self.mZygSupport.getNames()))
            if len(extra_names) > 0:
                eval_h.operationError(cond_data, "No sample(s) registered: "
                    + ' '.join(sorted(extra_names)))
                return None
        if len(p_group) == 0:
            eval_h.operationError(cond_data, "Problem group is empty")
            return None
        if len(cond_data[3]) == 0:
            eval_h.operationError(cond_data,
                "%s: empty set of variants" % self.getName())
            return None
        return {"p_group": p_group}

    def validateArgs(self, func_args):
        if func_args.get("problem_group"):
            if not isinstance(func_args["problem_group"], list):
                return "Problem group expected in form of set or list"
        return None

#===============================================
class CustomInheritanceUnit(FunctionUnit):

    @staticmethod
    def makeIt(ds_h, descr, before = None, after = None):
        unit_h = CustomInheritanceUnit(ds_h, descr)
        ds_h.getEvalSpace()._insertUnit(unit_h, before = before, after = after)

    def __init__(self, ds_h, descr):
        FunctionUnit.__init__(self, ds_h.getEvalSpace(), descr,
            sub_kind = "custom-inheritance-z", parameters = ["scenario"])
        self.mZygSupport = ds_h.getZygositySupport()

    def iterComplexCriteria(self, context, variants = None):
        if context is None:
            return
        if variants is None or "True" in variants:
            yield ("True",
                self.mZygSupport.conditionScenario(context["scenario"]))

    def makeInfoStat(self, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle["family"] = self.mZygSupport.getNames()
        ret_handle["affected"] = self.mZygSupport.getAffectedGroup()
        return ret_handle

    def makeParamStat(self, condition, parameters, eval_h, point_no):
        ret_handle = self.prepareStat()
        ret_handle.update(parameters)
        scenario = parameters.get("scenario")
        if not scenario:
            ret_handle["variants"] = None
            ret_handle["err"] = "Empty zygosity scenario"
        else:
            self.collectComplexStat(ret_handle, condition,
                {"scenario": scenario})
        return ret_handle

    def locateContext(self, cond_data, eval_h):
        scenario = cond_data[4].get("scenario")
        if not scenario:
            eval_h.operationError(cond_data, "Empty zygosity scenario")
            return None
        if len(cond_data[3]) == 0:
            eval_h.operationError(cond_data,
                "%s: empty set of variants" % self.getName())
            return None
        return {"scenario": scenario}

    def validateArgs(self, func_args):
        if func_args.get("scenario"):
            return self.mZygSupport.validateScenario(func_args["scenario"])
        return None

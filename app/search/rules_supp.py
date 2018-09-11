from StringIO import StringIO

from .flt_unit import BoolSetUnit
from app.eval.params import parseParams
#===============================================
class RulesEvalUnit(BoolSetUnit):
    def __init__(self, legend, rules_setup):
        BoolSetUnit.__init__(self, legend, "Rules",
            [func_h.getName() for func_h in rules_setup.FUNCTIONS])
        self.mRulesSetup = rules_setup
        self.mEnv = PresentationObj({param_h.getName(): param_h.getValue()
            for param_h in rules_setup.PARAMETERS})

    def iterExtractors(self):
        return iter([])

    def fillRulesPart(self, obj, data_record):
        rules_set = set()
        value_dict = {"Rules": rules_set}
        for unit in self.getLegend().iterUnits():
            if unit is not self:
                value_dict[unit.getName()] = unit.ruleValue(data_record)
        pre_rec = PresentationObj(value_dict)
        for idx, col in self.enumColumns():
            func_h = self.mRulesSetup.FUNCTIONS[idx]
            val = func_h.getFunc()(self.mEnv, pre_rec)
            col.setValues(data_record, val)
            if val:
                rules_set.add(func_h.getName())

    def getJSonData(self, expert_mode):
        ret = dict()
        columns = []
        for idx, col in self.enumColumns():
            func_h = self.mRulesSetup.FUNCTIONS[idx]
            if (not expert_mode and func_h.isExpert()):
                continue
            columns.append([func_h.getName(),
                self.mRulesSetup.getSrcContent(func_h.getFileName())])
        ret["columns"] = columns
        param_rep = StringIO()
        for param_h in self.mRulesSetup.PARAMETERS:
            if not expert_mode and param_h.isExpert():
                continue
            print >> param_rep, ("%s=%s" % (param_h.getName(),
                str(self.mEnv.get(param_h.getName()))))
        ret["params"] = param_rep.getvalue()
        return ret

    def modifyRulesData(self, expert_mode, item, content):
        if item == "--param":
            param_list = []
            for param_h in self.mRulesSetup.PARAMETERS:
                if not expert_mode and param_h.isExpert():
                    continue
                param_list.append(param_h.getName())
            result, error = parseParams(content, param_list)
        else:
            result, error = None, "Mode is not supported yet"
        if result is not None:
            for key, value in result:
                self.mEnv.set(key, value)
            return {"status": "OK"}
        return {"status": "FAILED", "error": error}

#===============================================
class PresentationObj:
    def __init__(self, value_dict):
        for key, value in value_dict.items():
            self.__dict__[key] = value

    def get(self, key):
        return self.__dict__.get(key)

    def set(self, key, value):
        self.__dict__[key] = value

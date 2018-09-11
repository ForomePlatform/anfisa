from StringIO import StringIO

from .flt_unit import BoolSetUnit
from app.eval.params import parseParams
#===============================================
class RulesEvalUnit(BoolSetUnit):
    def __init__(self, legend, rules_setup):
        BoolSetUnit.__init__(self, legend, "rules",
            [eval_info[0] for eval_info in rules_setup.FUNCTIONS])
        self.mRulesSetup = rules_setup
        self.mEnv = PresentationObj({key:val
            for key, val, expert_only in rules_setup.ATTRIBUTES})

    def iterExtractors(self):
        return iter([])

    def fillRulesPart(self, obj, data_record):
        rules_set = set()
        value_dict = {"rules": rules_set}
        for unit in self.getLegend().iterUnits():
            if unit is not self:
                val = unit.ruleValue(data_record)
                value_dict[unit.getName()] = val
                if val:
                    rules_set.add(unit.getName())
        pre_rec = PresentationObj(value_dict)
        for idx, col in self.enumColumns():
            val = self.mRulesSetup.FUNCTIONS[idx][1](
                self.mEnv, pre_rec)
            col.setValues(data_record, val)

    def getJSonData(self, expert_mode):
        ret = dict()
        columns = []
        for idx, col in self.enumColumns():
            if not expert_mode and self.mRulesSetup.FUNCTIONS[idx][3]:
                continue
            col_name = self.mRulesSetup.FUNCTIONS[idx][2]
            columns.append([self.mRulesSetup.FUNCTIONS[idx][0],
                col_name, self.mRulesSetup.getSrcContent(col_name)])
        ret["columns"] = columns
        param_rep = StringIO()
        for key, val, expert_only in self.mRulesSetup.ATTRIBUTES:
            if not expert_mode and expert_only:
                continue
            print >> param_rep, "%s=%s" %(key, str(self.mEnv.get(key)))
        ret["params"] = param_rep.getvalue()
        return ret

    def modifyRulesData(self, expert_mode, item, content):
        if item == "--param":
            param_list = []
            for key, val, expert_only in self.mRulesSetup.ATTRIBUTES:
                if not expert_mode and expert_only:
                    continue
                param_list.append(key)
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

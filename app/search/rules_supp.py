from StringIO import StringIO

from .flt_unit import MultiSetUnit
from app.eval.params import parseParams
from app.search.hot_eval import RULES_SETUP

#===============================================
class RulesEvalUnit(MultiSetUnit):
    sEnumNormValues = {
        "None": None,
        "null": None,
        "False": False,
        "false": False,
        "True": True,
        "true": True}
    @classmethod
    def normEnumValue(cls, val):
        return cls.sEnumNormValues.get(val, val)

    def __init__(self, index, dc_collection, unit_idx):
        MultiSetUnit.__init__(self, index, dc_collection, {
            "name": "Rules",
            "title": "Rules",
            "kind": "rules",
            "atomic": False,
            "compact": False,
            "default": None,
            "path": None,
            "research": False,
            "undef": 0,
            "variants": [[func_h.getName(), -1]
                for func_h in RULES_SETUP.FUNCTIONS]}, unit_idx)
        env_dict = {param_h.getName(): param_h.getValue()
            for param_h in RULES_SETUP.PARAMETERS}
        rules_data = (self.getIndex().getWS().getMongoWS().
            getRulesParamValues())
        if rules_data is not None:
            for key, val in rules_data:
                env_dict[key] = val
        self.mEnv = PresentationObj(env_dict)
        self.mUnitNames = None
        self.mMultiSetUnits = None

    def fillRecord(self, inp_data, record):
        pass

    def fillRulesPart(self, inp_data, data_record):
        if self.mUnitNames is None:
            self.mUnitNames = []
            self.mMultiSetUnits = set()
            for unit in self.getIndex().iterUnits():
                if unit is not self:
                    self.mUnitNames.append(unit.getName())
                    if not unit.isAtomic():
                        self.mMultiSetUnits.add(unit.getName())
        rules_set = set()
        value_dict = {"Rules": rules_set}
        for name in self.mUnitNames:
            val = inp_data.get(name)
            if val is None:
                if name in self.mMultiSetUnits:
                    val = set()
            elif isinstance(val, list):
                val = set(map(self.normEnumValue, val))
            elif isinstance(val, basestring):
                val = self.normEnumValue(val)
            value_dict[name] = val
        pre_rec = PresentationObj(value_dict)
        for idx, col in self.enumColumns():
            func_h = RULES_SETUP.FUNCTIONS[idx]
            val = func_h.getFunc()(self.mEnv, pre_rec)
            col.setValue(data_record, val)
            if val:
                rules_set.add(func_h.getName())

    def getJSonData(self, research_mode):
        ret = dict()
        columns = []
        for idx, col in self.enumColumns():
            func_h = RULES_SETUP.FUNCTIONS[idx]
            if (not research_mode and func_h.isResearch()):
                continue
            columns.append([func_h.getName(),
                RULES_SETUP.getSrcContent(func_h.getFileName())])
        ret["columns"] = columns
        param_rep = StringIO()
        for param_h in RULES_SETUP.PARAMETERS:
            if not research_mode and param_h.isResearch():
                continue
            print >> param_rep, ("%s=%s" % (param_h.getName(),
                str(self.mEnv.get(param_h.getName()))))
        ret["params"] = param_rep.getvalue()
        return ret

    def modifyRulesData(self, research_mode, item, content):
        if item == "--param":
            param_list = []
            for param_h in RULES_SETUP.PARAMETERS:
                if not research_mode and param_h.isResearch():
                    continue
                param_list.append(param_h.getName())
            rules_data, error = parseParams(content, param_list)
        else:
            rules_data, error = None, "Mode is not supported yet"
        if rules_data is None:
            return {"status": "FAILED", "error": error}
        for key, value in rules_data:
            self.mEnv.set(key, value)
        self.getIndex().getWS().getMongoWS().setRulesParamValues(
            rules_data)
        self.getIndex().updateRulesEnv()
        return {"status": "OK"}

#===============================================
class PresentationObj:
    def __init__(self, value_dict):
        for key, value in value_dict.items():
            self.__dict__[key] = value

    def get(self, key):
        return self.__dict__.get(key)

    def set(self, key, value):
        self.__dict__[key] = value

from StringIO import StringIO

from .flt_unit import BoolSetUnit
from app.eval.params import parseParams
#===============================================
class HotEvalUnit(BoolSetUnit):
    def __init__(self, legend, hot_setup):
        BoolSetUnit.__init__(self, legend, "hot",
            [eval_info[0] for eval_info in hot_setup.FUNCTIONS])
        self.mHotSetup = hot_setup
        self.mEnv = PresentationObj({key:val
            for key, val, expert_only in hot_setup.ATTRIBUTES})

    def iterExtractors(self):
        return iter([])

    def fillHotPart(self, obj, data_record):
        value_dict = dict()
        for unit in self.getLegend().iterUnits():
            if unit is not self:
                value_dict[unit.getName()] = unit.hotValue(data_record)
        pre_rec = PresentationObj(value_dict)
        for idx, col in self.iterColumns():
            val = self.mHotSetup.FUNCTIONS[idx][1](
                self.mEnv, pre_rec)
            col.setValues(data_record, val)

    def getTabData(self, data_record, expert_mode):
        ret = []
        for idx, col in self.iterColumns():
            if not expert_mode and self.mHotSetup.FUNCTIONS[idx][2]:
                continue
            ret.append((col.getName(), col.recordValue(data_record)))
        return ret

    def getJSonData(self, workspace, expert_mode):
        ret = {"workspace": "base"}
        columns = []
        for idx, col in self.iterColumns():
            if not expert_mode and self.mHotSetup.FUNCTIONS[idx][2]:
                continue
            col_name = self.mHotSetup.FUNCTIONS[idx][0]
            columns.append([col_name,
                self.mHotSetup.getSrcContent(col_name)])
        ret["columns"] = columns
        param_rep = StringIO()
        for key, val, expert_only in self.mHotSetup.ATTRIBUTES:
            if not expert_mode and expert_only:
                continue
            print >> param_rep, "%s=%s" %(key, str(self.mEnv.get(key)))
        ret["params"] = param_rep.getvalue()
        return ret

    def modifyHotData(self, workspace, expert_mode, item, content):
        if item == "--param":
            param_list = []
            for key, val, expert_only in self.mHotSetup.ATTRIBUTES:
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

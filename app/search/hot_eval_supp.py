from .flt_unit import BoolSetUnit

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

#===============================================
class PresentationObj:
    def __init__(self, value_dict):
        for key, value in value_dict.items():
            self.__dict__[key] = value



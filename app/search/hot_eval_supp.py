from .flt_unit import BoolSetUnit

#===============================================
class HotEvalUnit(BoolSetUnit):
    def __init__(self, legend, hot_eval_list):
        BoolSetUnit.__init__(self, legend, "hot",
            [eval_info[0] for eval_info in hot_eval_list])
        self.mHotEvalList = hot_eval_list

    def iterExtractors(self):
        return iter([])

    def fillHotPart(self, obj, data_record):
        value_dict = dict()
        for unit in self.getLegend().iterUnits():
            if unit is not self:
                value_dict[unit.getName()] = unit.hotValue(data_record)
        pre_rec = RecordPresentation(value_dict)
        for idx, col in self.iterColumns():
            val = self.mHotEvalList[idx][1](pre_rec)
            col.setValues(data_record, val)

    def getTabData(self, data_record):
        return [(col.getName(), col.recordValue(data_record))
            for idx, col in self.iterColumns()]

#===============================================
class RecordPresentation:
    def __init__(self, value_dict):
        for key, value in value_dict.items():
            self.__dict__[key] = value



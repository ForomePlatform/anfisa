import json
from copy import deepcopy

from app.model.solutions import STD_WS_FILTERS
from .column import DataColumnCollecton
from .flt_unit import loadWSFilterUnit
from .rules_supp import RulesEvalUnit
#===============================================
class Index:
    def __init__(self, ws_h):
        self.mWS = ws_h
        self.mDCCollection = DataColumnCollecton()
        self.mUnits = [RulesEvalUnit(self, self.mDCCollection, 0)]
        for unit_data in self.mWS.getFltSchema():
            unit = loadWSFilterUnit(self,
                self.mDCCollection, unit_data, len(self.mUnits))
            if unit is not None:
                self.mUnits.append(unit)
        self.mUnitDict = {unit.getName(): unit for unit in self.mUnits}
        assert len(self.mUnitDict) == len(self.mUnits)

        self.mRecords = []
        with self.mWS._openFData() as inp:
            for line in inp:
                inp_data = json.loads(line.decode("utf-8"))
                rec = self.mDCCollection.initRecord()
                for unit in self.mUnits:
                    unit.fillRecord(inp_data, rec)
                self.mUnits[0].fillRulesPart(inp_data, rec)
                self.mRecords.append(rec)
        assert len(self.mRecords) == self.mWS.getTotal()

        self.mStdFilters  = deepcopy(STD_WS_FILTERS)
        self.mFilterCache = dict()
        for filter_name, conditions in self.mStdFilters.items():
            self.cacheFilter(filter_name, conditions, None)

    def updateRulesEnv(self):
        with self.mWS._openFData() as inp:
            for rec_no, line in enumerate(inp):
                inp_data = json.loads(line.decode("utf-8"))
                self.mUnits[0].fillRulesPart(inp_data, self.mRecords[rec_no])
        to_update = []
        for filter_name, filter_info in self.mFilterCache.items():
            if any([cond_info[1] == "Rules"
                    for cond_info in filter_info[0]]):
                to_update.append(filter_name)
        for filter_name in to_update:
            filter_info = self.mFilterCache[filter_name]
            self.cacheFilter(filter_name, filter_info[0], filter_info[3])

    def getWS(self):
        return self.mWS

    def getUnit(self, unit_name):
        return self.mUnitDict[unit_name]

    def getRulesUnit(self):
        return self.mUnits[0]

    def iterUnits(self):
        return iter(self.mUnits)

    def hasStdFilter(self, filter_name):
        return filter_name in self.mStdFilters

    @staticmethod
    def not_NONE(val):
        return val is not None

    @staticmethod
    def numeric_LE(the_val):
        return lambda val: val is not None and val >= the_val

    @staticmethod
    def numeric_GE(the_val):
        return lambda val: val is not None and val <= the_val

    @staticmethod
    def numeric_LE_U(the_val):
        return lambda val: val is None or val >= the_val

    @staticmethod
    def numeric_GE_U(the_val):
        return lambda val: val is None or val <= the_val

    @staticmethod
    def enum_OR(base_idx_set):
        return lambda idx_set: len(idx_set & base_idx_set) > 0

    @staticmethod
    def enum_AND(base_idx_set):
        all_len = len(base_idx_set)
        return lambda idx_set: len(idx_set & base_idx_set) == all_len

    @staticmethod
    def enum_NOT(base_idx_set):
        return lambda idx_set: len(idx_set & base_idx_set) == 0

    @staticmethod
    def enum_ONLY(base_idx_set):
        return lambda idx_set: (len(idx_set) > 0 and
            len(idx_set - base_idx_set) == 0)

    def _applyCondition(self, rec_no_seq, cond_info):
        if cond_info[0] == "numeric":
            unit_name, ge_mode, the_val, use_undef = cond_info[1:]
            if ge_mode > 0:
                cmp_func = (self.numeric_GE_U(the_val) if use_undef
                    else self.numeric_GE(the_val))
            elif ge_mode == 0:
                cmp_func = (self.numeric_LE_U(the_val) if use_undef
                    else self.numeric_LE(the_val))
            elif use_undef is False:
                cmp_func = self.not_NONE
            cond_f = self.getUnit(unit_name).recordCondFunc(
                cmp_func)
        elif cond_info[0] == "enum":
            unit_name, filter_mode, variants = cond_info[1:]
            if filter_mode == "AND":
                enum_func = self.enum_AND
            elif filter_mode == "ONLY":
                enum_func = self.enum_ONLY
            elif filter_mode == "NOT":
                enum_func = self.enum_NOT
            else:
                enum_func = self.enum_OR
            cond_f = self.getUnit(unit_name).recordCondFunc(
                enum_func, variants)
        else:
            assert False
        flt_rec_no_seq = []
        for rec_no in rec_no_seq:
            if cond_f(self.mRecords[rec_no]):
                flt_rec_no_seq.append(rec_no)
        return flt_rec_no_seq

    def evalConditions(self, conditions):
        rec_no_seq = range(self.mWS.getTotal())[:]
        for cond_info in conditions:
            rec_no_seq = self._applyCondition(rec_no_seq, cond_info)
            if len(rec_no_seq) == 0:
                break
        return rec_no_seq

    def checkResearchBlock(self, conditions):
        for cond_info in conditions:
            if self.getUnit(cond_info[1]).checkResearchBlock(False):
                return True
        return False

    def cacheFilter(self, filter_name, conditions, time_label):
        self.mFilterCache[filter_name] = (
            conditions, self.evalConditions(conditions),
            self.checkResearchBlock(conditions), time_label)

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self, research_mode):
        ret = []
        for filter_name, flt_info in self.mFilterCache.items():
            if filter_name.startswith('_'):
                continue
            ret.append([filter_name, self.hasStdFilter(filter_name),
                research_mode or not flt_info[2], flt_info[3]])
        return sorted(ret)

    def makeStatReport(self, filter_name, research_mode,
            conditions = None):
        rec_no_seq = self.getRecNoSeq(filter_name, conditions)

        rec_seq = [self.mRecords[rec_no] for rec_no in rec_no_seq]

        stat_list = []
        for unit in self.mUnits:
            if not unit.checkResearchBlock(research_mode):
                stat_list.append(unit.collectStatJSon(rec_seq))

        report = {
            "stat-list": stat_list,
            "filter-list": self.getFilterList(research_mode),
            "cur-filter": filter_name}
        if (filter_name and filter_name in self.mFilterCache and
                not filter_name.startswith('_')):
            report["conditions"] = self.mFilterCache[filter_name][0]
        return report

    def getRecNoSeq(self, filter_name = None, conditions = None):
        if filter_name is None and conditions:
            return self.evalConditions(conditions)
        if filter_name in self.mFilterCache:
            return self.mFilterCache[filter_name][1]
        return range(self.mWS.getTotal())[:]

    def getRecFilters(self, rec_no, research_mode):
        ret0, ret1 = [], []
        for filter_name, flt_info in self.mFilterCache.items():
            if not research_mode and flt_info[2]:
                continue
            if (not filter_name.startswith('_') and
                    rec_no in flt_info[1]):
                if self.hasStdFilter(filter_name):
                    ret0.append(filter_name)
                else:
                    ret1.append(filter_name)
        return sorted(ret0) + sorted(ret1)

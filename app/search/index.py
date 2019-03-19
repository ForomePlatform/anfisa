import json, logging
from copy import deepcopy

from app.model.solutions import STD_WS_FILTERS
from app.model.a_config import AnfisaConfig
from .column import DataColumnCollecton
from .flt_unit import loadWSFilterUnit
from .rules_supp import RulesEvalUnit
#===============================================
class Index:
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

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
            self.cacheFilter(self.sStdFMark + filter_name,
                conditions, None)

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

    def goodOpFilterName(self, flt_name):
        return (flt_name and not flt_name.startswith(self.sStdFMark)
            and flt_name[0].isalpha() and ' ' not in flt_name)

    def hasStdFilter(self, filter_name):
        return filter_name in self.mStdFilters

    @staticmethod
    def numericFilterFunc(bounds, use_undef):
        bound_min, bound_max = bounds
        if bound_min is None:
            if bound_max is None:
                if use_undef:
                    return lambda val: val is None
                assert False
                return lambda val: True
            if use_undef:
                return lambda val: val is None or val <= bound_max
            return lambda val: val is not None and val <= bound_max
        if bound_max is None:
            if use_undef:
                return lambda val: val is None or bound_min <= val
            return lambda val: val is not None and bound_min <= val
        if use_undef:
            return lambda val: val is None or (
                bound_min <= val <= bound_max)
        return lambda val: val is not None and (
            bound_min <= val <= bound_max)

    @staticmethod
    def enumFilterFunc(filter_mode, base_idx_set):
        if filter_mode == "NOT":
            return lambda idx_set: len(idx_set & base_idx_set) == 0
        if filter_mode == "ONLY":
            return lambda idx_set: (len(idx_set) > 0 and
                len(idx_set - base_idx_set) == 0)
        if filter_mode == "AND":
            all_len = len(base_idx_set)
            return lambda idx_set: len(idx_set & base_idx_set) == all_len
        return lambda idx_set: len(idx_set & base_idx_set) > 0

    def _applyCondition(self, rec_no_seq, cond_info):
        cond_type, unit_name = cond_info[:2]
        unit_h = self.getUnit(unit_name)
        if cond_type in {"numeric", "int", "float"}:
            bounds, use_undef = cond_info[2:]
            filter_func = self.numericFilterFunc(bounds, use_undef)
        elif cond_info[0] in {"enum", "status"}:
            filter_mode, variants = cond_info[2:]
            filter_func = self.enumFilterFunc(filter_mode,
                unit_h.getVariantSet().makeIdxSet(variants))
        else:
            logging.error("Bad condition: %s" % json.dumps(cond_info))
            assert False
        cond_f = unit_h.recordCondFunc(filter_func)
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
            if self.hasStdFilter(filter_name):
                ret0.append(filter_name)
            elif self.goodOpFilterName(filter_name):
                ret1.append(filter_name)
        return sorted(ret0) + sorted(ret1)

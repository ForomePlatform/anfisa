import json
from copy import deepcopy

from app.config.a_config import AnfisaConfig
from app.config.solutions import Solutions
from app.filter.cond_op import CondOpEnv
from .column import DataColumnCollecton
from .flt_cond import WS_CondEnv
from .flt_unit import loadWSFilterUnit
from .rules_supp import RulesEvalUnit
#===============================================
class Index:
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, ws_h):
        self.mWS = ws_h
        self.mCondEnv = WS_CondEnv()
        self.mDCCollection = DataColumnCollecton()
        self.mUnits = [RulesEvalUnit(self, self.mDCCollection)]
        for unit_data in self.mWS.getFltSchema():
            unit_h = loadWSFilterUnit(self, self.mDCCollection, unit_data)
            if unit_h is not None:
                self.mUnits.append(unit_h)
        self.mUnitDict = {unit_h.getName(): unit_h
            for unit_h in self.mUnits}
        assert len(self.mUnitDict) == len(self.mUnits)
        for unit_h in self.mUnits:
            unit_h.setup()

        self.mRecords = []
        with self.mWS._openFData() as inp:
            for line in inp:
                inp_data = json.loads(line.decode("utf-8"))
                rec = self.mDCCollection.initRecord()
                for unit_h in self.mUnits:
                    unit_h.fillRecord(inp_data, rec)
                self.mUnits[0].fillRulesPart(inp_data, rec, len(self.mRecords))
                self.mRecords.append(rec)
        assert len(self.mRecords) == self.mWS.getTotal()

        self.mStdFilters = {self.sStdFMark + flt_name: deepcopy(cond_seq)
            for flt_name, cond_seq in Solutions.getWsFilters()}

        self.mFilterCache = dict()
        for filter_name, cond_seq in self.mStdFilters.items():
            self.cacheFilter(filter_name, cond_seq, None)

    def updateRulesEnv(self):
        with self.mWS._openFData() as inp:
            for rec_no, line in enumerate(inp):
                inp_data = json.loads(line.decode("utf-8"))
                self.mUnits[0].fillRulesPart(inp_data,
                    self.mRecords[rec_no], rec_no)
        to_update = []
        for filter_name, filter_info in self.mFilterCache.items():
            if any([cond_info[1] == "Rules"
                    for cond_info in filter_info[0].getCondSeq()]):
                to_update.append(filter_name)
        for filter_name in to_update:
            filter_info = self.mFilterCache[filter_name]
            self.cacheFilter(filter_name,
                filter_info[0].getCondSeq(), filter_info[3])

    def getWS(self):
        return self.mWS

    def getCondEnv(self):
        return self.mCondEnv

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

    def evalCondition(self, condition):
        rec_no_seq = []
        for rec_no in range(self.mWS.getTotal()):
            if condition(self.mRecords[rec_no]):
                rec_no_seq.append(rec_no)
        return rec_no_seq

    def _applyCondition(self, rec_no_seq, cond_seq):
        op_env = CondOpEnv(self.mCondEnv, None, cond_seq)
        condition = op_env.getResult()
        ret = []
        for rec_no in rec_no_seq:
            if condition(self.mRecords[rec_no]):
                ret.append(rec_no)
        return ret

    def checkResearchBlock(self, cond_seq):
        for cond_info in cond_seq:
            if self.getUnit(cond_info[1]).checkResearchBlock(False):
                return True
        return False

    def cacheFilter(self, filter_name, cond_seq, time_label):
        op_env = CondOpEnv(self.mCondEnv, None, cond_seq)
        self.mFilterCache[filter_name] = (
            op_env, self.evalCondition(op_env.getResult()),
            self.checkResearchBlock(cond_seq), time_label)

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
            op_env, repr_context):
        if filter_name in self.mFilterCache:
            op_env = self.mFilterCache[filter_name][0]
        condition = op_env.getResult()
        rec_no_seq = self.getRecNoSeq(filter_name, condition)
        rec_seq = [self.mRecords[rec_no] for rec_no in rec_no_seq]
        stat_list = []
        for unit_h, unit_comp in op_env.getActiveOperativeUnits():
            stat_list.append(unit_h.makeCompStat(
                condition, unit_comp, repr_context))
        for unit_h in self.mUnits:
            if (not unit_h.checkResearchBlock(research_mode) and
                    not unit_h.isScreened()):
                stat_list.append(unit_h.makeStat(rec_seq, repr_context))
        ret = {
            "total": self.mWS.getTotal(),
            "count": len(rec_seq),
            "stat-list": stat_list,
            "filter-list": self.getFilterList(research_mode),
            "cur-filter": filter_name,
            "conditions": op_env.getCondSeq()}
        op_env.report(ret, False)
        return ret

    def makeUnitStatReport(self, unit_name, condition, repr_context):
        rec_seq = [self.mRecords[rec_no]
            for rec_no in self.getRecNoSeq(None, condition)]
        return self.mUnitDict[unit_name].makeStat(rec_seq, repr_context)

    def getRecNoSeq(self, filter_name = None, condition = None):
        if filter_name is None and condition is not None:
            return self.evalCondition(condition)
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

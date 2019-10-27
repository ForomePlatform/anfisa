import json, logging
from copy import deepcopy
from io import TextIOWrapper

from utils.log_err import logException
from app.config.a_config import AnfisaConfig
from app.filter.cond_op import CondOpEnv
from app.model.comp_hets import CompHetsOperativeUnit
from app.config.solutions import modesToEnv
from .flt_cond import WS_CondEnv
from .flt_unit import loadWSFilterUnit
from .rules_supp import RulesEvalUnit
#===============================================
class Index:
    sStdFMark = AnfisaConfig.configOption("filter.std.mark")

    def __init__(self, ws_h):
        self.mWS = ws_h
        ds_modes = self.mWS.getDataInfo().get("modes")
        self.mCondEnv = WS_CondEnv(self.mWS.getName(), ds_modes)
        self.mCondEnv.addMode("WS")
        for mode in modesToEnv(self.mWS.getDataInfo()["meta"]):
            self.mCondEnv.addMode(mode)
        self.mUnits = [RulesEvalUnit(self)]
        depr_check_no_zeros = ds_modes and "secondary" in ds_modes
        for unit_data in self.mWS.getFltSchema():
            unit_h = loadWSFilterUnit(self, unit_data, depr_check_no_zeros)
            if unit_h is not None:
                self.mUnits.append(unit_h)
        self.mUnitDict = {unit_h.getName(): unit_h
            for unit_h in self.mUnits}
        assert len(self.mUnitDict) == len(self.mUnits)
        self.mStdFilterDict = None
        self.mStdFilterList = None
        self.mFilterCache = None

    def setup(self):
        with self.mWS._openFData() as inp:
            fdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(fdata_inp):
                inp_data = json.loads(line.strip())
                self.mCondEnv.addItemGroup(inp_data["$1"])
                for unit_h in self.mUnits:
                    unit_h.fillRecord(inp_data, rec_no)
                self.mUnits[0].fillRulesPart(inp_data, rec_no)
        self.mCondEnv.finishUp()
        for unit_h in self.mUnits:
            unit_h.setup()
        CompHetsOperativeUnit.setupCondEnv(self.mCondEnv, self.mWS)
        self.mStdFilterDict, self.mStdFilterList = dict(), []
        for flt_name, cond_seq in self.mCondEnv.getWsFilters():
            flt_name = self.sStdFMark + flt_name
            self.mStdFilterDict[flt_name] = deepcopy(cond_seq)
            self.mStdFilterList.append(flt_name)
        self.mFilterCache = dict()
        for filter_name, cond_seq in self.mStdFilterDict.items():
            self.cacheFilter(filter_name, cond_seq, None)

    def updateRulesEnv(self):
        with self.mWS._openFData() as inp:
            fdata_inp = TextIOWrapper(inp,
                encoding = "utf-8", line_buffering = True)
            for rec_no, line in enumerate(fdata_inp):
                inp_data = json.loads(line.strip())
                self.mUnits[0].fillRulesPart(inp_data, rec_no)
        to_update = []
        for filter_name, filter_info in self.mFilterCache.items():
            cond_seq = filter_info[0].getCondSeq()
            if any([cond_info[1] == "Rules" for cond_info in cond_seq]):
                to_update.append(filter_name)
        for filter_name in to_update:
            filter_info = self.mFilterCache[filter_name]
            if not self.cacheFilter(filter_name,
                    filter_info[0].getCondSeq(), filter_info[2]):
                logging.error("Filter %s for ws=%s failed" %
                    (filter_name, self.mWS.getName()))

    def getWS(self):
        return self.mWS

    def getCondEnv(self):
        return self.mCondEnv

    def getUnit(self, unit_name):
        return self.mUnitDict.get(unit_name)

    def getRulesUnit(self):
        return self.mUnits[0]

    def iterUnits(self):
        return iter(self.mUnits)

    def goodOpFilterName(self, flt_name):
        return (flt_name and not flt_name.startswith(self.sStdFMark)
            and flt_name[0].isalpha() and ' ' not in flt_name)

    def hasStdFilter(self, filter_name):
        return filter_name in self.mStdFilterDict

    def evalTotalCount(self, condition):
        if condition is None:
            return self.mWS.getTotal()
        return condition.countSelection()[0]

    def evalDetailedTotalCount(self, condition):
        if condition is None:
            return self.mCondEnv.getTotalCount()
        return condition.getSelectItemCount()

    def checkResearchBlock(self, cond_seq):
        for cond_info in cond_seq:
            unit_h = self.getUnit(cond_info[1])
            if unit_h is not None and unit_h.checkResearchBlock(False):
                return True
        return False

    def cacheFilter(self, filter_name, cond_seq, time_label):
        try:
            op_env = CondOpEnv(self.mCondEnv,
                None, cond_seq, name = filter_name)
            cond_entry = (op_env, self.checkResearchBlock(cond_seq),
                time_label)
        except:
            logException("Bad filter %s compilation for ws=%s" %
                (filter_name, self.mWS.getName()), error_mode = False)
            return False
        self.mFilterCache[filter_name] = cond_entry
        return True

    def dropFilter(self, filter_name):
        if filter_name in self.mFilterCache:
            del self.mFilterCache[filter_name]

    def getFilterList(self, research_mode):
        info_dict = dict()
        for filter_name, flt_info in self.mFilterCache.items():
            if filter_name.startswith('_'):
                continue
            flt_op_env, flt_research, flt_time_label = flt_info
            info_dict[filter_name] = [filter_name,
                self.hasStdFilter(filter_name),
                research_mode or not flt_research, flt_time_label]
        ret = []
        for filter_name in self.mStdFilterList:
            if filter_name in info_dict:
                ret.append(info_dict[filter_name])
                del info_dict[filter_name]
        return ret + [info_dict[filter_name]
            for filter_name in sorted(info_dict.keys())]

    def evalStat(self, unit_h, condition):
        return unit_h.makeStat(condition)[2]

    def getFilterOpEnv(self, filter_name):
        return self.mFilterCache[filter_name][0]

    def makeStatReport(self, op_env, research_mode, repr_context):
        condition = op_env.getResult()
        active_stat_list = []
        for unit_h, unit_comp in op_env.getActiveOperativeUnits():
            active_stat_list.append(unit_h.makeCompStat(
                condition, unit_comp, repr_context))
        stat_list = []
        for unit_h in self.mUnits:
            if (not unit_h.checkResearchBlock(research_mode) and
                    not unit_h.isScreened()):
                stat_list.append(unit_h.makeStat(condition, repr_context))
        for act_stat in active_stat_list:
            pos_ins = 0
            for idx, stat in enumerate(stat_list):
                if stat[1].get("vgroup") == act_stat[1].get("vgroup"):
                    pos_ins = idx + 1
            stat_list.insert(pos_ins, act_stat)
        count, count_items, total_items = condition.countSelection()
        ret = {
            "total": self.mWS.getTotal(),
            "count": count,
            "transcripts": [count_items, total_items],
            "stat-list": stat_list,
            "filter-list": self.getFilterList(research_mode),
            "cur-filter": op_env.getName(),
            "conditions": op_env.getCondSeq()}
        op_env.report(ret)
        return ret

    def makeUnitStatReport(self, unit_name, condition, repr_context):
        return self.mUnitDict[unit_name].makeStat(
            condition, repr_context)

    def getRecFilters(self, rec_no, research_mode):
        ret0, ret1 = [], []
        for filter_name, flt_info in self.mFilterCache.items():
            flt_op_env, flt_research, flt_time_label = flt_info
            if not research_mode and flt_research:
                continue
            if not flt_op_env.getResult().recInSelection(rec_no):
                continue
            if self.hasStdFilter(filter_name):
                ret0.append(filter_name)
            elif self.goodOpFilterName(filter_name):
                ret1.append(filter_name)
        return sorted(ret0) + sorted(ret1)

#import sys
from .path_works import AttrFuncPool
from .rules_supp import RulesEvalUnit
#===============================================
class FilterLegend:
    def __init__(self, name, rules_setup):
        self.mName     = name
        self.mFuncPool = AttrFuncPool()
        self.mColumns  = []
        self.mColDict  = dict()
        self.mUnitDict = dict()
        self.mIsOK     = False
        self.mUnits    = []
        self.mFilters  = dict()
        RulesEvalUnit(self, rules_setup)

    def _regColumnHandler(self, col_h):
        assert col_h.getName() not in self.mColDict
        col_idx = len(self.mColumns)
        self.mColDict[col_h.getName()] = col_h
        self.mColumns.append(col_h)
        return col_idx

    def _regUnit(self, unit):
        assert unit.getName() not in self.mUnitDict
        unit_idx = len(self.mUnits)
        self.mUnitDict[unit.getName()] = unit
        self.mUnits.append(unit)
        return unit_idx

    def regFilter(self, flt_name, conditions):
        self.mFilters[flt_name] = conditions

    def getName(self):
        return self.mName

    def getFuncPool(self):
        return self.mFuncPool

    def getColCount(self):
        return len(self.mColumns)

    def getColumn(self, col_name):
        return self.mColDict.get(col_name)

    def enumColumns(self):
        return enumerate(self.mColumns)

    def getUnitCount(self):
        return len(self.mUnits)

    def getUnit(self, name):
        return self.mUnitDict.get(name)

    def iterUnits(self):
        return iter(self.mUnits)

    def getRulesUnit(self):
        return self.mUnits[0]

    def isOK(self):
        return self.mIsOK

    def testDataSet(self, data_set):
        for obj in data_set.iterDataObjects():
            for unit in self.mUnits:
                unit.testValues(obj)

    def fillRecord(self, obj, record):
        for unit in self.mUnits:
            unit.fillRecord(obj, record)
        self.mUnits[0].fillRulesPart(obj, record)

    def updateRulesRecordPart(self, obj, record):
        self.mUnits[0].fillRulesPart(obj, record)

    def setup(self, rep_out):
        self.mIsOK = True
        for unit in self.mUnits:
            self.mIsOK != unit.setup(rep_out)
        return self.mIsOK

    def getStatusInfo(self):
        return ("Legend %s started %s: Units: %s, Columns: %d" %
            (self.mName, ["with problems", "successfuly"][self.mIsOK],
            len(self.mUnits), len(self.mColumns)))

    def collectStatJSon(self, data_records, expert_mode):
        ret = []
        for unit in self.mUnits:
            if not unit.checkExpertBlock(expert_mode):
                ret.append(unit.collectStatJSon(data_records))
        return ret

    def getFilterNames(self):
        return self.mFilters.keys()

    def hasFilter(self, flt_name):
        return flt_name in self.mFilters

    def getFilterConditions(self, flt_name):
        return self.mFilters.get(flt_name)

#import sys
from .path_works import AttrFuncPool

#===============================================
class FilterLegend:
    def __init__(self, name):
        self.mName       = name
        self.mFuncPool   = AttrFuncPool()
        self.mColumns    = []
        self.mColDict    = dict()
        self.mUnits    = []
        self.mUnitDict = dict()

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

    def getName(self):
        return self.mName

    def getFuncPool(self):
        return self.mFuncPool

    def getColCount(self):
        return len(self.mColumns)

    def getColumn(self, col_name):
        return self.mColDict.get(col_name)

    def iterColumns(self):
        return iter(self.mColumns)

    def getUnitCount(self):
        return len(self.mUnits)

    def getUnit(self, name):
        return self.mUnitDict.get(name)

    def iterUnits(self):
        return iter(self.mUnits)

    def testObj(self, obj):
        for unit in self.mUnits:
            unit.testValues(obj)

    def setup(self, rep_out):
        for unit in self.mUnits:
            unit.setup(rep_out)
        print >> rep_out, ("=Legend total = Units: %s, columns: %d" %
            (len(self.mUnits), len(self.mColumns)))

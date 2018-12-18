#import sys

from app.model.path_works import AttrFuncPool
from .column import DataColumnSet, DataCompactColumn
from .variants import VariantSet
#===============================================
class DataExtractor:
    def __init__(self, unit, name, path, val_conv,
            data_portion = None, compact_mode = False):
        self.mUnit   = unit
        self.mName   = name
        self.mPath   = path
        self.mPathF  = AttrFuncPool.makeFunc(
            self.mPath)
        self.mVConv  = val_conv
        self.mDataP  = data_portion
        self.mCompactMode = compact_mode
        assert (not self.mCompactMode or
            self.mDataP is None or self.mDataP.isCompact())

    def getLegend(self):
        return self.mLegend

    def getName(self):
        return self.mName

    def getPath(self):
        return self.mPath

    def getVConv(self):
        return self.mVConv

    def getDataP(self):
        return self.mDataP

    def getPathF(self):
        return self.mPathF

    def testValues(self, obj):
        return self.mVConv.testValues(self.mPathF(obj))

    def getVariantSet(self):
        return self.mVConv.getVariantSet()

    def setup(self, rep_out):
        print >> rep_out, "=Setup %s %s" % (
            self.mName, self.mVConv.getVarTypeCode())
        ret = self.mVConv.setup(rep_out)
        if ret is False:
            print >> rep_out, "=Bad conversion, rejected"
            if self.mDataP is not None:
                self.mDataP.setBad()
            return
        if self.mDataP is None:
            if self.mCompactMode:
                self.mDataP = DataCompactColumn(self.mUnit,
                    self.mName + ".#compact")
            else:
                self.mDataP = DataColumnSet(
                    self.mUnit, self.mName, self.mVConv.getVariantSet())

    def extract(self, obj, record):
        vv = self.mPathF(obj)
        values = self.mVConv.convert(vv)
        self.mDataP.setValues(record, values)

#===============================================
class DataGroupExtractor:
    def __init__(self, variants):
        self.mVariantSet = VariantSet(variants)
        self.mExtractors = []

    def _add(self, extr_h):
        self.mExtractors.append(extr_h)

    def getVariantSet(self):
        return self.mVariantSet

    def testValues(self, obj):
        is_ok = True
        for extr_h in self.mExtractors:
            is_ok |= extr_h.testValues(obj)
        return is_ok

    def setup(self, rep_out):
        for extr_h in self.mExtractors:
            extr_h.setup(rep_out)

    def extract(self, obj, record):
        for extr_h in self.mExtractors:
            extr_h.extract(obj, record)

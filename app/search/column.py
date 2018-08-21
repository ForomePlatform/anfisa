#import sys
import abc

#===============================================
class DataPortion:
    ATOM_DATA_TYPE_BOOL  = 1
    ATOM_DATA_TYPE_INT   = 2
    ATOM_DATA_TYPE_FLOAT = 3

    def __init__(self, filter_unit, name):
        self.mFilterUnit = filter_unit
        self.mName       = name

    def getFilterUnit(self):
        return self.mFilterUnit

    def getName(self):
        return self.mName

    def isAtomic(self):
        return True

    def isCompact(self):
        return False

    @abc.abstractmethod
    def setValues(self, record, value):
        pass

#===============================================
class DataColumn(DataPortion):
    def __init__(self, filter_unit, name, atom_type):
        DataPortion.__init__(self, filter_unit, name)
        self.mAtomType = atom_type
        self.mColIdx  = self.getFilterUnit().getLegend()._regColumnHandler(
            self)

    def setBad(self):
        self.mColIdx = -1

    def isBad(self):
        return self.mColIdx >= 0

    def getColIdx(self):
        return self.mColIdx

    def getAtomType(self):
        return self.mAtomType

    def setValues(self, record, value):
        assert self.mColIdx >= 0
        record[self.mColIdx] = value

    def recordValue(self, data_record):
        return data_record[self.mColIdx]

#===============================================
class DataColumnSet(DataPortion):
    def __init__(self, filter_unit, name, variant_set):
        DataPortion.__init__(self, filter_unit, name)
        self.mVariantSet = variant_set
        self.mColumns = [DataColumn(self.getFilterUnit(),
            "%s/%s" % (name, variant), self.ATOM_DATA_TYPE_BOOL)
            for variant in iter(self.mVariantSet)]

    def isAtomic(self):
        return False

    def setBad(self):
        for col in self.mColumns:
            col.setBad()

    def isBad(self):
        return any([col.isBad() for col in self.mColumns])

    def setValues(self, record, values):
        for value in values:
            self.mColumns[value].setValues(record, True)

    def recordValues(self, data_record):
        ret = set()
        for var_no, col in enumerate(self.mColumns):
            if col.recordValue(data_record):
                ret.add(var_no)
        return ret

#===============================================
class DataCompactColumn(DataColumn):
    def __init__(self, filter_unit, name):
        DataColumn.__init__(self, filter_unit, name, self.ATOM_DATA_TYPE_INT)
        self.mPackSetDict = dict()
        self.mPackSetSeq  = []

    def isAtomic(self):
        return True

    def isCompact(self):
        return True

    @classmethod
    def makePackKey(cls, idx_set):
        return '#'.join(map(str, sorted(idx_set)))

    def setValues(self, record, idx_set):
        key = self.makePackKey(idx_set)
        idx = self.mPackSetDict.get(key)
        if idx is None:
            idx = len(self.mPackSetSeq)
            self.mPackSetDict[key] = idx
            self.mPackSetSeq.append(sorted(idx_set))
        DataColumn.setValues(self, record, idx)

    def getSetByIdx(self, idx):
        if 0 <= idx < len(self.mPackSetSeq):
            return self.mPackSetSeq[idx]
        return None

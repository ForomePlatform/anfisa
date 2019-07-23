#===============================================
class DataColumnCollecton:
    ATOM_DATA_TYPE_BOOL  = 1
    ATOM_DATA_TYPE_INT   = 2
    ATOM_DATA_TYPE_FLOAT = 3

    @classmethod
    def ATOM_TYPE_NUM(cls, kind):
        if kind == "float":
            return cls.ATOM_DATA_TYPE_FLOAT
        return cls.ATOM_DATA_TYPE_INT

    def __init__(self):
        self.mColumns = []

    def __len__(self):
        return len(self.mColumns)

    def initRecord(self):
        return [None] * len(self.mColumns)

    def makeColumn(self, filter_unit, name, atom_type):
        ret = DataColumn(filter_unit, name, atom_type, len(self.mColumns))
        self.mColumns.append(ret)
        return ret

    def makeColumnSet(self, filter_unit, name, variants):
        columns = []
        for variant in variants:
            columns.append(self.makeColumn(filter_unit,
                "%s/%s" % (name, variant), self.ATOM_DATA_TYPE_BOOL))
        return DataColumnSet(filter_unit, name, columns)

    def makeCompactEnumColumn(self, filter_unit, name):
        ret = DataCompactColumn(filter_unit, name, len(self.mColumns))
        self.mColumns.append(ret)
        return ret

#===============================================
class DataPortion:
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

#===============================================
class DataColumn(DataPortion):
    def __init__(self, filter_unit, name, atom_type, col_idx):
        DataPortion.__init__(self, filter_unit, name)
        self.mAtomType = atom_type
        self.mColIdx   = col_idx
        assert self.mColIdx >= 0

    def getAtomType(self):
        return self.mAtomType

    def setValue(self, record, value):
        record[self.mColIdx] = value

    def recordValue(self, data_record):
        return data_record[self.mColIdx]

#===============================================
class DataColumnSet(DataPortion):
    def __init__(self, filter_unit, name, columns):
        DataPortion.__init__(self, filter_unit, name)
        self.mColumns = columns

    def isAtomic(self):
        return False

    def __iter__(self):
        return iter(self.mColumns)

    def setValues(self, record, values):
        for value in values:
            self.mColumns[value].setValue(record, True)

    def recordValues(self, data_record):
        ret = set()
        for var_no, col in enumerate(self.mColumns):
            if col.recordValue(data_record):
                ret.add(var_no)
        return ret

#===============================================
class DataCompactColumn(DataColumn):
    def __init__(self, filter_unit, name, col_idx):
        DataColumn.__init__(self, filter_unit, name,
            DataColumnCollecton.ATOM_DATA_TYPE_INT, col_idx)
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
        DataColumn.setValue(self, record, idx)

    def recordValues(self, data_record):
        idx = self.recordValue(data_record)
        if idx is not None and 0 <= idx < len(self.mPackSetSeq):
            return set(self.mPackSetSeq[idx])
        return set()

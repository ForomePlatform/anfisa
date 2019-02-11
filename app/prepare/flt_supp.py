from zlib import crc32
from app.model.path_works import AttrFuncPool
#===============================================
class SuportFilterField:
    @staticmethod
    def create(field_info):
        fld_name, fld_kind = field_info[:2]

        if fld_kind == 'rec-no':
            assert len(field_info) == 2
            return SupportFieldRecNo(fld_name)
        if fld_kind == 'hash':
            assert len(field_info) == 3
            return SupportFieldHash(fld_name, field_info[2])
        if fld_kind == 'path':
            assert len(field_info) == 3
            return SupportFieldPath(fld_name, field_info[2])
        if fld_kind == "path-seq":
            assert len(field_info) > 4
            return SupportFieldPathSeq(fld_name, field_info[2], field_info[3:])

#===============================================
class SupportFieldRecNo:
    def __init__(self, name):
        self.mName = name

    def process(self, rec_no, rec_data, result):
        result[self.mName] = rec_no

#===============================================
class SupportFieldHash:
    def __init__(self, name, base_name):
        self.mName = name
        self.mBaseName = base_name

    def process(self, rec_no, rec_data, result):
        result[self.mName] = crc32(result[self.mBaseName]) % (1<<32)

#===============================================
class SupportFieldPath:
    def __init__(self, name, path):
        self.mName = name
        self.mFunc = AttrFuncPool.makeFunc(path)

    def process(self, rec_no, rec_data, result):
        res = self.mFunc(rec_data)
        if res:
            result[self.mName] = res[0]

#===============================================
class SupportFieldPathSeq:
    def __init__(self, name, separator, path_seq):
        self.mName = name
        self.mSeparator = separator
        self.mFuncSeq = [AttrFuncPool.makeFunc(path)
            for path in path_seq]

    def process(self, rec_no, rec_data, result):
        result[self.mName] = self.mSeparator.join(
            map(str, [func(rec_data)[0] for func in self.mFuncSeq]))

from zlib import crc32

from utils.path_works import AttrFuncPool
#===============================================
class PresentationFieldHash:
    def __init__(self, name, base_name):
        self.mName = name
        self.mBaseName = base_name

    def process(self, rec_data, result):
        result[self.mName] = crc32(
            bytes(result[self.mBaseName], 'utf-8')) % (1<<32)

#===============================================
class PresentationFieldPath:
    def __init__(self, name, path):
        self.mName = name
        self.mFunc = AttrFuncPool.makeFunc(path)

    def process(self, rec_data, result):
        res = self.mFunc(rec_data)
        result[self.mName] = res[0] if res else None

#===============================================
class PresentationFieldPathSeq:
    def __init__(self, name, separator, path_seq):
        self.mName = name
        self.mSeparator = separator
        self.mFuncSeq = [AttrFuncPool.makeFunc(path)
            for path in path_seq]

    def process(self, rec_data, result):
        result[self.mName] = self.mSeparator.join(
            map(str, [func(rec_data)[0] for func in self.mFuncSeq]))

#===============================================
class PresentationData:
    sFields = [
        PresentationFieldPath("_color", "/data/color_code"),
        PresentationFieldPath("_label", "/data/label"),
        PresentationFieldPathSeq("_key", '-',
            ["/data/seq_region_name", "/data/start", "/data/end"]),
        PresentationFieldHash("_rand", "_key")]

    @classmethod
    def make(cls, rec_data):
        result = dict()
        for fld in cls.sFields:
            fld.process(rec_data, result)
        return result


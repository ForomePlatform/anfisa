import re

#===============================================
class AttrChunker:
    def __init__(self, separators):
        self.mSeparators = separators
        self.mRegExp = re.compile(separators)

    def apply(self, values):
        ret = set()
        for value in values:
            for v in re.split(self.mRegExp, value):
                if v:
                    ret.add(v)
        return ret

import codecs
from md5 import md5

#===============================================
def codeHash(tree_code):
    return md5(tree_code.strip()).hexdigest()

#===============================================
class SolutionItem:
    def __init__(self, kind, name, data, requires,
            used_names, ext_name = None):
        self.mKind = kind
        self.mName = name
        self.mRequires = requires
        self.mData = data
        use_name = ext_name if ext_name else self.mName
        assert use_name not in used_names
        used_names.add(use_name)

    def testIt(self, kind, test_f):
        if kind is not None and self.mKind != kind:
            return False
        return test_f(self.mRequires)

    def getName(self):
        return self.mName

    def getData(self):
        return self.mData

#===============================================
class SolutionPack:
    @classmethod
    def readFile(cls,fname):
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            return inp.read()
        assert False

    @classmethod
    def readFileSeq(cls, fnames):
        return "\n".join([cls.readFile(fname) for fname in fnames])

    @classmethod
    def readListFile(cls, fname):
        ret = []
        with codecs.open(fname, "r", encoding = "utf-8") as inp:
            for line in inp:
                val = line.partition('#')[0].strip()
                if val:
                    ret.append(val)
        return ret

    #===============================================
    sPacks = dict()

    @classmethod
    def regPack(cls, solution_pack):
        assert solution_pack.getName() not in cls.sPacks
        cls.sPacks[solution_pack.getName()] = solution_pack

    @classmethod
    def regDefaultPack(cls, solution_pack):
        assert None not in cls.sPacks
        cls.sPacks[None] = solution_pack

    @classmethod
    def select(cls, name = None):
        return cls.sPacks[name]

    #===============================================
    def __init__(self, name):
        self.mName = name
        self.mItems = []
        self.mUsedNames = set()
        self.mTreeCodes = dict()

    def getName(self):
        return self.mName

    def regFilterWS(self, flt_name, cond_seq, requires = None):
        self.mItems.append(SolutionItem("flt_ws", flt_name,
            cond_seq, requires, self.mUsedNames))

    def regFilterXL(self, flt_name, cond_seq, requires = None):
        self.mItems.append(SolutionItem("flt_xl", flt_name,
            cond_seq, requires, self.mUsedNames))

    def regTreeCode(self, code_name, fname_seq, requires = None):
        tree_code = self.readFileSeq(fname_seq)
        it = SolutionItem("tree_code", code_name,
            tree_code, requires, self.mUsedNames)
        self.mItems.append(it)
        self.mTreeCodes[codeHash(tree_code)] = it

    def regPanel(self, unit_name, panel_name, fname, requires = None):
        self.mItems.append(SolutionItem("panel", unit_name,
            (panel_name, self.readListFile(fname)), requires,
            self.mUsedNames, unit_name + "/" + panel_name))

    def iterItems(self, kind, test_f):
        for it in self.mItems:
            if it.testIt(kind, test_f):
                yield it

    def getTreeByHashCode(self, hash_code):
        return self.mTreeCodes.get(hash_code)


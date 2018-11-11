from app.model.types import Types
#===============================================
class AttrH:
    sBaseHostFrom = None
    sBaseHostTo   = None

    @classmethod
    def setupBaseHostReplacement(cls, host_from, host_to):
        cls.sBaseHostFrom = host_from
        cls.sBaseHostTo   = host_to

    @classmethod
    def getJSonOptions(cls):
        return {"link_host": [cls.sBaseHostFrom, cls.sBaseHostTo]}

    @classmethod
    def normLink(cls, str):
        if cls.sBaseHostFrom and str:
            return str.replace(cls.sBaseHostFrom, cls.sBaseHostTo)
        return str

    def __init__(self, name, kind = None, title = None,
            is_seq = False, tp_cnt = None):
        self.mName = name
        self.mTitle = (title if title is not None else name)
        self.mKinds = kind.split() if kind else ["norm"]
        self.mIsSeq = is_seq
        self.mResearchOnly = "research" in self.mKinds
        self.mPath = None
        self.mTpCnt = tp_cnt

    def copy(self):
        assert self.mTpCnt is None
        return AttrH(self.mName, " ".join(self.mKinds), self.mTitle,
            self.mIsSeq)

    def _setTpCnt(self, tp_cnt):
        self.mTpCnt = tp_cnt

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def isSeq(self):
        return self.mIsSeq

    def hasKind(self, kind):
        return kind in self.mKinds

    def getType(self):
        return Types.filterTypeKind(self.mKinds)

    def getMainKind(self):
        return self.mKinds[0]

    def getPath(self):
        return self.mPath

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getTpCnt(self):
        return self.mTpCnt

    def getJSonObj(self):
        return {
            "name": self.mName, "kind": " ".join(self.mKinds),
            "title": self.mTitle, "is_seq": self.mIsSeq,
            "cnt": self.mTpCnt.repJSon() if self.mName is not None else None,
            "path": self.mPath}

    def _feedAttrPath(self, path, registry):
        if self.mName is None:
            self.mPath = "None"
            return
        a_path = path + '/' + self.mName
        self.mPath = a_path
        registry.add(a_path)
        if self.mIsSeq:
            registry.add(a_path + "[]")
        if "json" in self.mKinds or "hidden" in self.mKinds:
            registry.add(a_path + "*")
            return

    def _checkTpCnt(self):
        rep = None
        tp, sub_tp = self.mTpCnt.detectTypePair()
        if self.mIsSeq:
            if tp != "list":
                rep = "Option is_seq dropped"
                self.mIsSeq = False
            else:
                tp = sub_tp
        else:
            if tp == "list":
                rep = "Option is_seq set up"
                self.mIsSeq = True
                tp = sub_tp
        if self.hasKind("link") and tp not in (
                "undef", "null", "link", "empty"):
            if not rep:
                rep = ""
            else:
                rep += "/ "
            rep += "Option link dropped"
            self.mKinds.remove("link")
            if len(self.mKinds) == 0:
                self.mKinds.append("norm")
        return rep



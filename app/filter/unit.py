#===============================================
class Unit:
    def __init__(self, descr, unit_kind = None):
        self.mDescr = descr
        self.mUnitKind  = descr["kind"] if unit_kind is None else unit_kind
        if self.mUnitKind == "long":
            self.mUnitKind = "int"
        self.mName  = descr["name"]
        self.mTitle = descr["title"]
        self.mNo    = descr["no"]
        self.mVGroup = descr.get("vgroup")
        self.mResearchOnly = descr["research"]
        self.mRenderMode = descr.get("render")
        self.mToolTip = descr.get("tooltip")
        self.mScreened = False

    def setup(self):
        pass

    def getUnitKind(self):
        return self.mUnitKind

    def getName(self):
        return self.mName

    def getDescr(self):
        return self.mDescr

    def getTitle(self):
        return self.mTitle

    def getVGroup(self):
        return self.mVGroup

    def getToolTip(self):
        return self.mToolTip

    def getNo(self):
        return self.mNo

    def isScreened(self):
        return self.mScreened

    def _setScreened(self, value = True):
        self.mScreened = value

    def prepareStat(self):
        ret = [self.mUnitKind, {
            "name": self.mName,
            "vgroup": self.mVGroup}]
        if self.mTitle and self.mTitle != self.mName:
            ret[1]["title"] = self.mTitle
        if self.mRenderMode:
            ret[1]["render"] = self.mRenderMode
        if self.mToolTip:
            ret[1]["tooltip"] = self.mToolTip
        return ret

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

#===============================================
class DraftUnit:
    def __init__(self, name, rec_func = None):
        self.mName = name
        self.mRecFunc = rec_func

    def getName(self):
        return self.mName

    def getRecVal(self, rec_no):
        return self.mRecFunc(rec_no)

    def isDetailed(self):
        return False

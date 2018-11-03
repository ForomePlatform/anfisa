#===============================================
class AspectH:
    def __init__(self, name, title, source, field = None,
            attrs = None, ignored = False, col_groups = None,
            research_only = False):
        self.mName     = name
        self.mTitle    = title
        self.mSource   = source
        self.mField    = field
        self.mAttrs    = attrs
        self.mIgnored  = ignored
        self.mResearchOnly = research_only
        self.mColGroups = col_groups
        assert self.mSource in ("view", "data")
        if self.mColGroups is not None:
            assert self.mField is None
        if self.mIgnored and self.mAttrs is None:
            self.mAttrs = []
        self.mTpCnt = None

    def copy(self):
        assert self.mTpCnt is None
        return AspectH(self.mName, self.mTitle, self.mSource, self.mField,
            [attr_h.copy() for attr_h in self.mAttrs], self.mIgnored,
            self.mColGroups, self.mResearchOnly)

    def _setTpCnt(self, tp_cnt):
        self.mTpCnt = tp_cnt

    def _addAttr(self, attr_h):
        self.mAttrs.append(attr_h)

    def getName(self):
        return self.mName

    def getSource(self):
        return self.mSource

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return self.mAttrs

    def getField(self):
        return self.mField

    def getColGroups(self):
        return self.mColGroups

    def getTpCnt(self):
        return self.mTpCnt

    def isIgnored(self):
        return self.mIgnored

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getAspectKind(self):
        return {"view": "norm", "data": "tech"}[self.mSource]

    def setRecommendedAttrs(self, attrs):
        self.mAttrs = attrs

    def _feedAttrPath(self, registry):
        path_seq = ['/' + self.mSource]
        registry.add(path_seq[0])
        if self.mField:
            path_seq[0] += '/' + self.mField
            registry.add(path_seq[0])
        if self.mColGroups is not None:
            grp_path_seq = []
            for idx in range(self.mColGroups.getCount()):
                grp_attr = self.mColGroups.getAttr(idx)
                grp_path_seq.append(path_seq[0][:])
                grp_path_seq[-1] += '/' + grp_attr
                registry.add(grp_path_seq[-1])
                grp_path_seq[-1] += '[]'
                registry.add(grp_path_seq[-1])
            path_seq = grp_path_seq
        for path in path_seq:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)

    def getJSonObj(self):
        ret = {
            "name": self.mName, "title": self.mTitle, "source": self.mSource,
            "field": self.mField, "ignored": self.mIgnored,
            "research": self.mResearchOnly,
            "attrs": [attr_h.getJSonObj() for attr_h in self.mAttrs]}
        if self.mColGroups is not None:
            ret["col_groups"] = self.mColGroups.getJSonObj()
        return ret

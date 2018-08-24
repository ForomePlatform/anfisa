#===============================================
class AspectH:
    def __init__(self, name, title, json_container = False, attrs = None,
            ignored = False, kind = None, col_groups = None):
        self.mName     = name
        self.mTitle    = title
        self.mJsonContainer = (self.mName
            if json_container is False else json_container)
        self.mAttrs = (attrs if attrs else [])
        self.mIgnored  = ignored
        self.mKind = kind if kind else "norm"
        self.mColGroups = col_groups

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getJsonContainer(self):
        return self.mJsonContainer

    def getAttrs(self):
        return self.mAttrs

    def getColGroups(self):
        return self.mColGroups

    def isIgnored(self):
        return self.mIgnored

    def getAspectKind(self):
        return self.mKind

    def _feedAttrPath(self, registry):
        path = self.mJsonContainer
        if path is None:
            path = ""
        else:
            path = "/" + path
            registry.add(path)
        if self.mColGroups is not None:
            for grp in self.mColGroups:
                grp_path = path + '/' + grp.getAttr()
                registry.add(grp_path)
                grp_path += "[]"
                registry.add(grp_path)
                for attr in self.mAttrs:
                    attr._feedAttrPath(grp_path, registry)
        else:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)


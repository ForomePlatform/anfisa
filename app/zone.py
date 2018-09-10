#===============================================
class ZoneH:
    def __init__(self, workspace, title):
        self.mWS = workspace
        self.mTitle = title

    def _setTitle(self, title):
        self.mTitle = title

    def getWS(self):
        return self.mWS

    def getTitle(self):
        return self.mTitle

    def makeValuesReport(self):
        return {
            "zone": self.getName(),
            "title": self.getTitle(),
            "variants": self.getVariants()}

#===============================================
class FilterZoneH(ZoneH):
    def __init__(self, workspace, title, unit):
        ZoneH.__init__(self, workspace, title)
        self.mUnit = unit

    def getName(self):
        return self.mUnit.getName()

    def getVariants(self):
        return [var for var in self.mUnit.getVariantSet()]

    def restrict(self, rec_no_seq, variants):
        return self.getWS().getIndex()._applyCrit(rec_no_seq,
            ("enum", self.mUnit.getName(), "OR", variants))

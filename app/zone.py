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


#===============================================
class FilterZoneH(ZoneH):
    def __init__(self, workspace, title, unit):
        ZoneH.__init__(self, workspace, title)
        self.mUnit = unit

    def getName(self):
        return self.mUnit.getName()

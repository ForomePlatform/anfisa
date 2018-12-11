from .rest import RestAgent
from .xl_unit import XL_Unit

#===============================================
class XL_Legend:
    def __init__(self, xlref, query_url):
        self.mXLRef = xlref
        self.mQueryAgent = RestAgent(query_url)
        self.mDataSource = self.mXLRef["datasource"]
        self.mUnits = []
        for descr in self.mXLRef["units"]:
            self.mUnits.append(XL_Unit.create(self, descr))

    def getQueryAgent(self):
        return self.mQueryAgent

    def getDataSource(self):
        return self.mDataSource

    def report(self, output):
        for unit in self.mUnits:
            unit.report(output)

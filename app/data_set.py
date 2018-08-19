#import sys
import abc

#===============================================
class DataSet:
    def __init__(self, name):
        self.mName = name

    def getName(self):
        return self.mName

    @abc.abstractmethod
    def reportList(self, output):
        print >> output, '<p>list of records here</p>'

    @abc.abstractmethod
    def getNRecords(self):
        return None

    @abc.abstractmethod
    def getRecKey(self, rec_no):
        return None

    @abc.abstractmethod
    def getRecord(self, rec_key):
        return None

    @abc.abstractmethod
    def getFirstAspectID(self):
        return None

    def testLegend(self, legend):
        for rec_no in range(self.getNRecords()):
            legend.testObj(self.getRecord(rec_no).getObj())

#===============================================
class DataRecord:
    @abc.abstractmethod
    def getID(self):
        return None

    @abc.abstractmethod
    def reportIt(self, output):
        pass

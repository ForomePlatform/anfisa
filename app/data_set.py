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
    def getRecID(self, rec_no):
        return None

    @abc.abstractmethod
    def getRecord(self, rec_id):
        return None

#===============================================
class DataRecord:
    @abc.abstractmethod
    def getID(self):
        return None

    @abc.abstractmethod
    def reportIt(self, output):
        pass


#import sys
from .data_a_json import DataSet_AJson

#===============================================
class AnfisaData:
    sConfig = None
    sSets = dict()
    sDefaultSetName = None

    @classmethod
    def setup(cls, config):
        cls.sConfig = config
        for nd in config.xpath("/conf/data/dataset"):
            set_name = nd.get("name")
            if cls.sDefaultSetName is None:
                cls.sDefaultSetName = set_name
            if nd.get("kind") == "a-json":
                cls.sSets[set_name] = DataSet_AJson(set_name, nd.get("file"))
            else:
                assert False

    @classmethod
    def getSet(cls, set_name = None):
        if set_name is None:
            set_name = cls.sDefaultSetName
        return cls.sSets.get(set_name)

    @classmethod
    def reportSets(cls, cur_set, output):
        print >> output, ('<select id="data_set" value="%s">' %
            cur_set.getName())
        for set_name in sorted(cls.sSets.keys()):
            d_set = cls.sSets[set_name]
            print >> output, ' <option value="%s">%s</option>' % (
                d_set.getName(), d_set.getName())
        print >> output, '</select>'


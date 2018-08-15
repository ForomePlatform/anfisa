import sys, logging
from app.data_a_json import DataSet_AJson
from app.search.cfg_flt_a_json import LEGEND_AJson
#===============================================
logging.basicConfig(level = 10)
data_fname = sys.argv[1]

print >> sys.stderr, "Testing filter legend for dataset:", data_fname

data_set = DataSet_AJson("data-set", data_fname)

for rec_no in range(data_set.getNRecords()):
    LEGEND_AJson.testObj(data_set.getRecord(rec_no).getObj())

LEGEND_AJson.setup(sys.stderr)

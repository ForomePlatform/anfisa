import sys, logging
from app.view.dataset import DataSet
from app.view_setup import ViewSetup
from app.search_setup import MainLegend
#===============================================
logging.basicConfig(level = 10)
data_fname = sys.argv[1]

print >> sys.stderr, "Testing filter legend for dataset:", data_fname

data_set = DataSet(ViewSetup, "data-set", data_fname)

for rec_no in range(data_set.getSize()):
    MainLegend.testObj(data_set.getRecord(rec_no).getObj())

MainLegend.setup(sys.stderr)

print >> sys.stderr, MainLegend.getStatusInfo()

import sys, logging
from app.view.dataset import DataSet
from app.view_setup import ViewSetup
from app.search_setup import prepareLegend
#===============================================
logging.basicConfig(level = 10)
data_fname = sys.argv[1]

print >> sys.stderr, "Testing filter legend for dataset:", data_fname

data_set = DataSet(ViewSetup, "data-set", data_fname)

legend = prepareLegend("ws")
legend.testDataSet(data_set)
legend.setup(sys.stderr)

print >> sys.stderr, legend.getStatusInfo()

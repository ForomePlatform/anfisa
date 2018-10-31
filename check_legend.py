import sys, logging
from app.view.dataset import DataSet
from app.view.checker import ViewDataChecker
from app.view_setup import ViewSetup
from app.view_cfg import setupRecommended
from app.search_setup import prepareLegend
#===============================================
logging.basicConfig(level = 0)
data_fname = sys.argv[1]

print >> sys.stderr, "Testing filter legend for dataset:", data_fname

setupRecommended()
data_set = DataSet(ViewSetup(), "data-set", data_fname)

ViewDataChecker.check(data_set.getViewSetup(), data_set, 2)

legend = prepareLegend("ws")
legend.testDataSet(data_set)
legend.setup(sys.stdout)

print >> sys.stdout, legend.getStatusInfo()

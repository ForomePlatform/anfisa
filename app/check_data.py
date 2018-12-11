import sys, logging
from argparse import ArgumentParser

from app.view.dataset import DataSet
from app.view.checker import ViewDataChecker
from app.view_setup import ViewSetup
from app.view_cfg import setupRecommended
from app.search_setup import prepareLegend

#===============================================
parser = ArgumentParser()

parser.add_argument("-m", "--mode", type = str,
    default = "check", help = "Mode: check")
parser.add_argument("dataset", type = str, nargs="?",
    help = "Dataset file")
args = parser.parse_args()

#===============================================
logging.basicConfig(level = 0)
setupRecommended()
legend = prepareLegend("ws")
#===============================================

if args.mode == "check":
    print >> sys.stderr, "Testing filter legend for dataset:", \
        args.dataset
    data_set = DataSet(ViewSetup(), "data-set", args.dataset)
    ViewDataChecker.check(data_set.getViewSetup(), data_set, 2)
    legend.testDataSet(data_set)
    legend.setup(sys.stdout)
    print >> sys.stdout, legend.getStatusInfo()

else:
    print >> sys.stderr, "Bad mode:", args.mode

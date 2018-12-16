import sys, logging, json, codecs

from argparse import ArgumentParser
from app.view_cfg import setupRecommended
from app.search_setup import prepareLegend

from app.xl.druid import DruidCfg
from app.xl.rest import RestAgent
from app.xl.xl_prep import XL_Preparator
from app.xl.xl_dataset import XL_Dataset
#===============================================
parser = ArgumentParser()

parser.add_argument("-m", "--mode", type = str,
    default = "report", help = "Mode: create/drop/report")
parser.add_argument("-d", "--datasource", type = str,
    default = "anfisa-exp", help = "Druid datasource")
parser.add_argument("-t", "--time", type = str,
    default = "2015-01-01", help = "Load timestart")
parser.add_argument("-w", "--work_dir", type = str,
    default = ".", help = "Work directory")
parser.add_argument("-D", "--datadescr", type = str,
    default = "xl-set.js", help = "XL dataset descriptor file")
parser.add_argument("--druid_index", type = str,
    default = DruidCfg.INDEX_URL, help = "Druid hostname")
parser.add_argument("--druid_query", type = str,
    default = DruidCfg.QUERY_URL, help = "Druid hostname")
parser.add_argument("--druid_coord", type = str,
    default = DruidCfg.COORD_URL, help = "Druid hostname")
parser.add_argument("dataset", type = str, nargs="?",
    help = "Dataset file")
args = parser.parse_args()

#===============================================
logging.basicConfig(level = 0)
setupRecommended()
legend = prepareLegend("ws")

#===============================================
if args.mode == "create":
    print >> sys.stderr, "Prepare load data for dataset:", \
        args.dataset

    print >> sys.stderr, "Setup legend..."
    with codecs.open(args.dataset, "r", encoding = "utf-8") as inp:
        for line in inp:
            legend.testDataRec(json.loads(line))
    legend.setup(sys.stderr)

    xl_prep = XL_Preparator(legend, args.datasource, args.work_dir, args.time)

    print >> sys.stderr, "Preparing data", xl_prep.getOutFileName()
    with codecs.open(xl_prep.getOutFileName(), "w",
            encoding = "utf-8") as outp:
       with codecs.open(args.dataset, "r", encoding = "utf-8") as inp:
            for line in inp:
                rec_in = json.loads(line)
                rec_out = xl_prep.procRecord(rec_in)
                print >> outp, json.dumps(rec_out)

    print >> sys.stderr, "Load to Druid", args.datasource
    index_agent = RestAgent(args.druid_index)
    ret = index_agent.call(xl_prep.getExtSchema())

    print >> sys.stderr, "Storing XL dataset descriptor:", args.datadescr
    with codecs.open(args.datadescr, "w", encoding = "utf-8") as outp:
        print >> outp, json.dumps(xl_prep.makeIntSchema())

    print >> sys.stderr, "Done:", json.dumps(ret)

elif args.mode == "drop":
    coord_agent = RestAgent(args.druid_coord)
    coord_agent.call(None, "DELETE", "/datasources/" + args.datasource)

    index_agent = RestAgent(args.druid_index)
    ret = index_agent.call({
        "type": "kill",
        "dataSource": args.datasource,
        "interval" : DruidCfg.INTERVAL})

elif args.mode == "report":
    xl_ds = XL_Dataset(args.datadescr, "xl", "XL-Exp", args.druid_query)
    xl_ds.report(sys.stdout)

else:
    print >> sys.stderr, "Bad mode:", args.mode

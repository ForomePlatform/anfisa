import sys, os, logging, json, codecs, gzip, subprocess

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
    help = "Druid datasource")
parser.add_argument("-c", "--config", type = str,
    help = "xl-adm configuration")
parser.add_argument("input_dataset", type = str, nargs="?",
    help = "Dataset file")

args = parser.parse_args()

#===============================================
with codecs.open(args.config, "r", encoding = "utf-8") as inp:
    cfg = json.loads(inp.read())

#===============================================
logging.basicConfig(level = 0)
setupRecommended()
legend = prepareLegend("ws")

lines_period = cfg["lines_report_period"]
#===============================================
if args.mode == "create":
    print >> sys.stderr, "Prepare load data for dataset:", \
        args.input_dataset

    print >> sys.stderr, "Setup legend..."
    with codecs.open(args.input_dataset, "r", encoding = "utf-8") as inp:
        line_no = 0
        for line in inp:
            legend.testDataRec(json.loads(line))
            line_no += 1
            if (line_no % lines_period) == 0:
                print >> sys.stderr, "\t", line_no, "lines..."
        print >> sys.stderr, "\tTotal:", line_no, "lines."
    legend.setup(sys.stderr)

    xl_prep = XL_Preparator(legend, args.datasource,
        cfg.get("final_data", cfg["inter_data"]),
        cfg["time-start"])

    print >> sys.stderr, "Preparing data", cfg["inter_data"]
    with gzip.open(cfg["inter_data"], 'wb') as outp:
        with codecs.open(args.input_dataset,
                "r", encoding = "utf-8") as inp:
            line_no = 0
            for line in inp:
                rec_in = json.loads(line)
                rec_out = xl_prep.procRecord(rec_in)
                print >> outp, json.dumps(rec_out).encode("utf-8")
                line_no += 1
                if (line_no % lines_period) == 0:
                    print >> sys.stderr, "\t", line_no, "lines..."

    if cfg.get("final_data") is not None:
        cmd = [cfg["scp"]]
        if cfg.get("scp-key"):
            cmd += ["-i", os.path.expanduser(cfg["scp-key"])]
        cmd.append(cfg["inter_data"])
        cmd.append(cfg["scp-host"] + ':' + cfg["final_data"])
        print >> sys.stderr, "Remote copying:", ' '.join(cmd)
        subprocess.call(cmd)

    print >> sys.stderr, "Load to Druid", args.datasource
    index_agent = RestAgent(cfg["druid_url_index"])
    ret = index_agent.call(xl_prep.getExtSchema())

    target_fname = cfg["target_descr"] % args.datasource
    print >> sys.stderr, "Storing XL dataset descriptor:", target_fname
    with codecs.open(target_fname, "w", encoding = "utf-8") as outp:
        print >> outp, json.dumps(xl_prep.makeIntSchema())

    print >> sys.stderr, "Done:", json.dumps(ret)

elif args.mode == "drop":
    coord_agent = RestAgent(cfg["druid_url_coord"])
    coord_agent.call(None, "DELETE", "/datasources/" + args.datasource)

    index_agent = RestAgent(cfg["druid_url_index"])
    ret = index_agent.call({
        "type": "kill",
        "dataSource": args.datasource,
        "interval" : DruidCfg.INTERVAL})

elif args.mode == "report":
    target_fname = cfg["target_descr"] % args.datasource
    xl_ds = XL_Dataset(target_fname, "xl", cfg["druid_url_query"])
    xl_ds.report(sys.stdout)

else:
    print >> sys.stderr, "Bad mode:", args.mode

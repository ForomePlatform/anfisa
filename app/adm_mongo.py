import sys, codecs, json
from argparse import ArgumentParser
from copy import deepcopy
from pymongo import MongoClient

#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin.detach())
sys.stderr = codecs.getwriter('utf8')(sys.stderr.detach())
sys.stdout = codecs.getwriter('utf8')(sys.stdout.detach())
#===============================================
parser = ArgumentParser()
parser.add_argument("-H", "--host",  default = "localhost",
    help = "MongoDB host")
parser.add_argument("-P", "--port",  type = int, default = 27017,
    help = "MongoDB port")
parser.add_argument("-d", "--database", default = "Anfisa",
    help = "Anfisa database in MongoDB")
parser.add_argument("-c", "--config",
    help = "Anfisa config file(anfisa.json), "
        "use it instead of host/port/database")
parser.add_argument("-C", "--config_default", action = "store_true",
    help = "Use it for config = ./anfisa.json")
parser.add_argument("command", nargs="+",
    help="Commands, use help command for list")
run_args = parser.parse_args()

#===============================================
def readContent(content):
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj is None or isinstance(obj, str):
            continue
        yield obj

def updateMRec(agent, obj):
    set_data = dict()
    for key, val in obj.items():
        if key == '_id':
            obj_id = val
        else:
            set_data[key] = val
    agent.update({'_id': obj_id}, {"$set": set_data}, upsert = True)

#===============================================
def cleanRecordTags(it):
    rec = deepcopy(it)
    for sub_tags in rec['_h'][1]:
        if '_id' in sub_tags:
            del sub_tags['_id']
    return rec

def _filterTagState(state, tag_name):
    ret = dict()
    for key, value in state.items():
        if not key.startswith('_') and key != tag_name:
            ret[key] = value
    return json.dumps(ret, sort_keys = True)

def clearRecordOneTag(rec, tag_name, out_seq):
    if tag_name not in rec and all(tag_name not in sub_tags
            for sub_tags in rec['_h'][1]):
        return
    rec_id = rec['_id']
    base_idx = rec['_h'][0]
    hist_seq = [_filterTagState(state, tag_name)
        for state in rec['_h'][1]]
    if base_idx >= len(hist_seq):
        base_idx = len(hist_seq)
        hist_seq.append(_filterTagState(rec, tag_name))
    idx = 1
    while idx < len(hist_seq):
        if hist_seq[idx - 1] == hist_seq[idx]:
            del hist_seq[idx]
            if base_idx >= idx:
                base_idx -= 1
        else:
            idx += 1
    hist_seq = [json.loads(descr) for descr in hist_seq]
    if len(hist_seq) == 1 and len(hist_seq[0]) == 0:
        out_seq.append((rec_id, None))
        return
    set_data = deepcopy(hist_seq[base_idx])
    if base_idx + 1 == len(hist_seq):
        del hist_seq[base_idx]
    set_data['_h'] = [base_idx, hist_seq]
    instr = {"$set": set_data}
    if tag_name in rec:
        instr["$unset"] = {tag_name: ""}
    out_seq.append((rec_id, instr))

#===============================================
class CmdInfo:
    sCmdList = []

    def __init__(self, name, args = "ds", create_support = False):
        self.mName = name
        self.mArgs = args
        self.mCreateSupp = create_support
        self.sCmdList.append(self)

    def getDSName(self, cmd_seq):
        if len(self.mArgs) > 0 and self.mArgs[0] == "ds":
            return cmd_seq[1]
        return None

    def hasCreateSupport(self):
        return self.mCreateSupp

    def checkArgs(self, cmd_seq):
        if len(cmd_seq) < 1 or cmd_seq[0] != self.mName:
            return None
        if len(self.mArgs) > 0 and self.mArgs[-1] == "datafile":
            if len(cmd_seq) == 1 + len(self.mArgs):
                with open(cmd_seq[-1], "r", encoding = "utf-8") as inp:
                    content = inp.read()
                cmd_seq[-1] = content
                return cmd_seq
            elif len(cmd_seq) == len(self.mArgs):
                content = sys.stdin.read()
                cmd_seq.append(content)
                return cmd_seq
            print("Improper call arguments", file = sys.stderr)
            return False
        if len(cmd_seq) == 1 + len(self.mArgs):
            return cmd_seq
        print("Improper call arguments", file = sys.stderr)
        return False

    def report(self, output):
        print("\t%s %s" % (self.mName, " ".join(self.mArgs)), file = output)

    @classmethod
    def reportAll(cls, output):
        for cmd_info in cls.sCmdList:
            cmd_info.report(output)

    @classmethod
    def checkCall(cls, cmd_seq):
        for cmd_info in cls.sCmdList:
            ret = cmd_info.checkArgs(cmd_seq)
            if ret is not None:
                return (ret, cmd_info.getDSName(cmd_seq),
                    cmd_info.hasCreateSupport())
        print("Command not supported", file = sys.stderr)
        return False, None, None

#===============================================
CmdInfo("ds-list", [], True)
CmdInfo("filter-list", ["ds"], True)
CmdInfo("tag-list", ["ds"], True)
CmdInfo("dump-filters", ["ds"], True)
CmdInfo("dump-tags", ["ds"], True)
CmdInfo("dump-rules", ["ds"], True)
CmdInfo("load-tags", ["ds", "datafile"], create_support = True)
CmdInfo("load-filters", ["ds", "datafile"], create_support = True)
CmdInfo("load-rules", ["ds", "datafile"], create_support = True)
CmdInfo("del-filter", ["ds", "filter_name"])
CmdInfo("del-tag", ["ds", "tag_name"])
CmdInfo("drop-filters", ["ds"])
CmdInfo("drop-tags", ["ds"])
CmdInfo("drop-rules", ["ds"])
CmdInfo("drop-ds", ["ds"])

#===============================================
if run_args.command[0] == "help":
    print(' ===Anfisa/MongoDB administration tool===', file = sys.stderr)
    print(' * List of commands *', file = sys.stderr)
    CmdInfo.reportAll(sys.stderr)
    sys.exit()
cmd_seq, ds_name, cr_supp = CmdInfo.checkCall(run_args.command)
if not cmd_seq:
    sys.exit()

if run_args.config_default:
    config_path = "./anfisa.json"
else:
    config_path = run_args.config
if config_path:
    with open(config_path, "r", encoding = "utf-8") as inp:
        cfg = json.loads(inp.read())
    database = cfg["mongo-db"]
    host, port = cfg.get("mongo-host"), cfg.get("mongo-port")
else:
    database = run_args.database
    host, port = run_args.host,  run_args.port

mongo = MongoClient(host,  port)
if ds_name is not None:
    m_db = mongo[database]
    if ds_name not in m_db.list_collection_names():
        if cr_supp:
            print("DS %s is possibly creating" % ds_name,
                file = sys.stderr)
        else:
            print("DS not found", ds_name, file = sys.stderr)
            sys.exit()
    m_ds = m_db[ds_name]
else:
    m_db = mongo[database]

#===============================================
if cmd_seq[0] == "ds-list":
    ret = []
    for coll_name in m_db.list_collection_names():
        if coll_name != "system.indexes":
            ret.append(coll_name)
    print(json.dumps(ret))
    sys.exit()

#===============================================
if cmd_seq[0] == "filter-list":
    ret = []
    for it in m_ds.find({'_tp' : "flt"}):
        it_name = it['_id']
        if it_name.startswith("flt-"):
            ret.append(it_name[4:])
    print(json.dumps(ret, sort_keys = True, indent = 4))
    sys.exit()

#===============================================
if cmd_seq[0] == "tag-list":
    ret = set()
    for it in m_ds.find():
        if not it['_id'].startswith("rec-"):
            continue
        for key in it.keys():
            if not key.startswith('_'):
                ret.add(key)
    print(json.dumps(sorted(ret)))
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-filters":
    ret = []
    for it in m_ds.find({'_tp' : "flt"}):
        it_name = it['_id']
        if it_name.startswith("flt-"):
            ret.append(deepcopy(it))
    for rec in ret:
        print(json.dumps(rec))
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-tags":
    ret = []
    for it in m_ds.find():
        if not it['_id'].startswith("rec-"):
            continue
        ret.append(cleanRecordTags(it))
    for rec in ret:
        print(json.dumps(rec))
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-rules":
    ret = None
    it = m_ds.find_one({'_id': 'params'})
    if it is not None:
        ret = deepcopy(it["params"])
    print(json.dumps(ret))
    sys.exit()

#===============================================
if cmd_seq[0] == "load-filters":
    cnt = 0
    for instr in readContent(cmd_seq[2]):
        assert instr['_tp'] == "flt"
        updateMRec(m_ds, instr)
        cnt += 1
    print(json.dumps("FILTERS LOADED: %d" % cnt))
    sys.exit()

#===============================================
if cmd_seq[0] == "load-tags":
    cnt = 0
    for instr in readContent(cmd_seq[2]):
        assert instr['_id'].startswith("rec-")
        updateMRec(m_ds, instr)
        cnt += 1
    print(json.dumps("TAGS LOADED: %d" % cnt))
    sys.exit()

#===============================================
if cmd_seq[0] == "load-rules":
    cnt = 0
    for data in readContent(cmd_seq[2]):
        assert all([len(pair) == 2 for pair in data])
        m_ds.update({'_id': "params"},
            {"$set": {'params': data}}, upsert = True)
        cnt += 1
    print(json.dumps("RULES LOADED: %d" % cnt))
    sys.exit()

#===============================================
if cmd_seq[0] == "del-filter":
    filter_name = cmd_seq[2]
    m_ds.remove({'_id': "flt-" + filter_name})
    print(json.dumps("FILTER %s DELETED" % filter_name))
    sys.exit()

#===============================================
if cmd_seq[0] == "del-tag":
    tag_name = cmd_seq[2]
    seq_update = []
    for it in m_ds.find():
        if it['_id'].startswith("rec-"):
            clearRecordOneTag(it, tag_name, seq_update)
    for rec_id, instr in seq_update:
        if instr is not None:
            m_ds.update({'_id': rec_id}, instr, upsert = True)
        else:
            m_ds.remove({'_id': rec_id})
    print(json.dumps("TAG %s DELETED: %d records" %
        (tag_name, len(seq_update))))
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-filters":
    m_ds.remove({'_tp': "flt"})
    print(json.dumps("FILTERS DROPPED"))
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-tags":
    m_ds.remove({'_id': {"$regex": "^rec-"}})
    print(json.dumps("TAGS DROPPED"))
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-rules":
    m_ds.remove({'_id': 'params'})
    print(json.dumps("RULES PARAMS DROPPED"))
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-ds":
    m_ds.drop()
    print(json.dumps("DATASET DROPPED"))
    sys.exit()

#===============================================
print("Oops: command not supported", file = sys.stderr)


import sys, codecs, json
from argparse import ArgumentParser
from copy import deepcopy
from pymongo import MongoClient

#=====================================
sys.stdin  = codecs.getreader('utf8')(sys.stdin)
sys.stderr = codecs.getwriter('utf8')(sys.stderr)
sys.stdout = codecs.getwriter('utf8')(sys.stdout)
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
parser.add_argument("-l", "--legacy", action = "store_true",
    help = "Legacy storage mode")
parser.add_argument("command", nargs="+",
    help="Commands, use help command for list")
run_args = parser.parse_args()

#===============================================
def reportLegacy():
    print >> sys.stdout, '"Legacy mode: -l"'

def readContent(content):
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
        obj = json.loads(line)
        if obj is None or isinstance(obj, basestring):
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
def clearRecordTags(it, legacy_mode):
    rec = deepcopy(it)
    if legacy_mode:
        rec['_id'] = "rec-" + rec['_id']
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
    if tag_name not in rec and all([tag_name not in sub_tags
            for sub_tags in rec['_h'][1]]):
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

    def __init__(self, name, args = "ws", legacy_support = False,
            create_support = False):
        self.mName = name
        self.mArgs = args
        self.mLegacySupp = legacy_support
        self.mCreateSupp = create_support
        self.sCmdList.append(self)

    def getWSName(self, cmd_seq):
        if len(self.mArgs) > 0 and self.mArgs[0] == "ws":
            return cmd_seq[1]
        return None

    def hasCreateSupport(self):
        return self.mCreateSupp

    def checkArgs(self, cmd_seq, legacy_mode):
        if len(cmd_seq) < 1 or cmd_seq[0] != self.mName:
            return None
        if legacy_mode and not self.mLegacySupp:
            print >> sys.stderr, "No legacy mode for command"
            return False
        if len(self.mArgs) > 0 and self.mArgs[-1] == "datafile":
            if len(cmd_seq) == 1 + len(self.mArgs):
                with codecs.open(cmd_seq[-1], "r", encoding = "utf-8") as inp:
                    content = inp.read()
                cmd_seq[-1] = content
                return cmd_seq
            elif len(cmd_seq) == len(self.mArgs):
                content = sys.stdin.read()
                cmd_seq.append(content)
                return cmd_seq
            print >> sys.stderr, "Improper call arguments"
            return False
        if len(cmd_seq) == 1 + len(self.mArgs):
            return cmd_seq
        print >> sys.stderr, "Improper call arguments"
        return False

    def report(self, output):
        legacy_msg = "(legacy supported)" if self.mLegacySupp else ""
        print >> output, "\t%s %s %s" % (
            self.mName, " ".join(self.mArgs), legacy_msg)

    @classmethod
    def reportAll(cls, output):
        for cmd_info in cls.sCmdList:
            cmd_info.report(output)

    @classmethod
    def checkCall(cls, cmd_seq, legacy_mode):
        for cmd_info in cls.sCmdList:
            ret = cmd_info.checkArgs(cmd_seq, legacy_mode)
            if ret is not None:
                return (ret, cmd_info.getWSName(cmd_seq),
                    cmd_info.hasCreateSupport())
        print >> sys.stderr, "Command not supported"
        return False, None, None

#===============================================
CmdInfo("ws-list", [], True)
CmdInfo("filter-list", ["ws"], True)
CmdInfo("tag-list", ["ws"], True)
CmdInfo("dump-filters", ["ws"], True)
CmdInfo("dump-tags", ["ws"], True)
CmdInfo("dump-rules", ["ws"], True)
CmdInfo("load-tags", ["ws", "datafile"], create_support = True)
CmdInfo("load-filters", ["ws", "datafile"], create_support = True)
CmdInfo("load-rules", ["ws", "datafile"], create_support = True)
CmdInfo("del-filter", ["ws", "filter_name"])
CmdInfo("del-tag", ["ws", "tag_name"])
CmdInfo("drop-filters", ["ws"])
CmdInfo("drop-tags", ["ws"])
CmdInfo("drop-rules", ["ws"])
CmdInfo("drop-ws", ["ws"])

#===============================================
if run_args.command[0] == "help":
    print >> sys.stderr, ' ===Anfisa/MongoDB administation tool==='
    print >> sys.stderr, ' * List of commands *'
    CmdInfo.reportAll(sys.stderr)
    sys.exit()
cmd_seq, ws_name, cr_supp = CmdInfo.checkCall(
    run_args.command, run_args.legacy)
if not cmd_seq:
    sys.exit()

if run_args.config_default:
    config_path = "./anfisa.json"
else:
    config_path = run_args.config
if config_path:
    with codecs.open(config_path, "r", encoding = "utf-8") as inp:
        cfg = json.loads(inp.read())
    database = cfg["mongo-db"]
    host, port = cfg.get("mongo-host"), cfg.get("mongo-port")
else:
    database = run_args.database
    host, port = run_args.host,  run_args.port

mongo = MongoClient(host,  port)
if ws_name is not None:
    if run_args.legacy:
        if ws_name not in mongo.list_database_names():
            print >> sys.stderr, "No such (legacy) db:", ws_name
            sys.exit()
        m_ws_l = mongo[ws_name]
    else:
        m_db = mongo[database]
        if ws_name not in m_db.list_collection_names():
            if cr_supp:
                print >> sys.stderr, ("Workspace %s is possibly creating" %
                    ws_name)
            else:
                print >> sys.stderr, "So such workspace:", ws_name
                sys.exit()
        m_ws = m_db[ws_name]
elif not run_args.legacy:
    m_db = mongo[database]

#===============================================
if cmd_seq[0] == "ws-list":
    ret = []
    if run_args.legacy:
        reportLegacy()
        for db_name in mongo.list_database_names():
            if len(set(mongo[db_name].list_collection_names()) &
                {'rec_data', 'filters', 'common'}) > 0:
                ret.append(db_name)
    else:
        for coll_name in m_db.list_collection_names():
            is_ws = False
            for it in m_db[coll_name].find():
                if it.get('_tp') == "flt" or (
                        '_id' in it and it['_id'].startswith("rec-")):
                    is_ws = True
                    break
            if is_ws:
                ret.append(coll_name)
    print >> sys.stdout, json.dumps(ret)
    sys.exit()

#===============================================
if cmd_seq[0] == "filter-list":
    ret = []
    if run_args.legacy:
        reportLegacy()
        for it in m_ws_l["filters"].find():
            ret.append(it['_id'])
    else:
        for it in m_ws.find({'_tp' : "flt"}):
            it_name = it['_id']
            if it_name.startswith("flt-"):
                ret.append(it_name[4:])
    print >> sys.stdout, json.dumps(ret, sort_keys = True, indent = 4)
    sys.exit()

#===============================================
if cmd_seq[0] == "tag-list":
    ret = set()
    if run_args.legacy:
        reportLegacy()
        for it in m_ws_l["rec_data"].find():
            for key in it.keys():
                if not key.startswith('_'):
                    ret.add(key)
    else:
        for it in m_ws.find():
            if not it['_id'].startswith("rec-"):
                continue
            for key in it.keys():
                if not key.startswith('_'):
                    ret.add(key)
    print >> sys.stdout, json.dumps(sorted(ret))
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-filters":
    ret = []
    if run_args.legacy:
        reportLegacy()
        for it in m_ws_l["filters"].find():
            rec = deepcopy(it)
            rec['_id'] = "flt-" + rec['_id']
            rec['_tp'] = "flt"
            ret.append(rec)
    else:
        for it in m_ws.find({'_tp' : "flt"}):
            it_name = it['_id']
            if it_name.startswith("flt-"):
                ret.append(deepcopy(it))
    for rec in ret:
        print >> sys.stdout, json.dumps(rec)
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-tags":
    ret = []
    if run_args.legacy:
        reportLegacy()
        for it in m_ws_l["rec_data"].find():
            ret.append(clearRecordTags(it, True))
    else:
        for it in m_ws.find():
            if not it['_id'].startswith("rec-"):
                continue
            ret.append(clearRecordTags(it, False))
    for rec in ret:
        print >> sys.stdout, json.dumps(rec)
    sys.exit()

#===============================================
if cmd_seq[0] == "dump-rules":
    ret = None
    if run_args.legacy:
        reportLegacy()
        it = m_ws_l["common"].find_one({'_id': '_params'})
        if it is not None:
            ret = deepcopy(it["params"])
    else:
        it = m_ws.find_one({'_id': 'params'})
        if it is not None:
            ret = deepcopy(it["params"])
    print >> sys.stdout, json.dumps(ret)
    sys.exit()

#===============================================
if cmd_seq[0] == "load-filters":
    cnt = 0
    for instr in readContent(cmd_seq[2]):
        assert instr['_tp'] == "flt"
        updateMRec(m_ws, instr)
        cnt += 1
    print >> sys.stdout, json.dumps("FILTERS LOADED: %d" % cnt)
    sys.exit()

#===============================================
if cmd_seq[0] == "load-tags":
    cnt = 0
    for instr in readContent(cmd_seq[2]):
        assert instr['_id'].startswith("rec-")
        updateMRec(m_ws, instr)
        cnt += 1
    print >> sys.stdout, json.dumps("TAGS LOADED: %d" % cnt)
    sys.exit()

#===============================================
if cmd_seq[0] == "load-rules":
    cnt = 0
    for data in readContent(cmd_seq[2]):
        assert all([len(pair) == 2 for pair in data])
        m_ws.update({'_id': "params"},
            {"$set": {'params': data}}, upsert = True)
        cnt += 1
    print >> sys.stdout, json.dumps("RULES LOADED: %d" % cnt)
    sys.exit()

#===============================================
if cmd_seq[0] == "del-filter":
    filter_name = cmd_seq[2]
    m_ws.remove({'_id': "flt-" + filter_name})
    print >> sys.stdout, json.dumps("FILTER %s DELETED" % filter_name)
    sys.exit()

#===============================================
if cmd_seq[0] == "del-tag":
    tag_name = cmd_seq[2]
    seq_update = []
    for it in m_ws.find():
        if it['_id'].startswith("rec-"):
            clearRecordOneTag(it, tag_name, seq_update)
    for rec_id, instr in seq_update:
        if instr is not None:
            m_ws.update({'_id': rec_id}, instr, upsert = True)
        else:
            m_ws.remove({'_id': rec_id})
    print >> sys.stdout, json.dumps("TAG %s DELETED: %d records" %
        (tag_name, len(seq_update)))
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-filters":
    m_ws.remove({'_tp': "flt"})
    print >> sys.stdout, json.dumps("FILTERS DROPPED")
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-tags":
    m_ws.remove({'_id': {"$regex": "^rec-"}})
    print >> sys.stdout, json.dumps("TAGS DROPPED")
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-rules":
    m_ws.remove({'_id': 'params'})
    print >> sys.stdout, json.dumps("RULES PARAMS DROPPED")
    sys.exit()

#===============================================
if cmd_seq[0] == "drop-ws":
    m_ws.delete_many({})
    print >> sys.stdout, json.dumps("DATASET DROPPED")
    sys.exit()

#===============================================
print >> sys.stderr, "Oops: command not supported"


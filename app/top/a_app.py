import sys, os, json, logging, signal
from io import StringIO

from app.config.view_schema import defineViewSchema
from app.config.a_config import AnfisaConfig
from app.config.solutions import prepareSolutions
from app.model.rest_api import RestAPI
from app.model.mongo_db import MongoConnector
from app.model.data_vault import DataVault
from app.prepare.v_check import ViewDataChecker
from app.filter.druid_agent import DruidAgent
from app.view.attr import AttrH
from app.view.asp_set import AspectSetH
from export.excel import ExcelExport
from int_ui.mirror_dir import MirrorUiDirectory
from int_ui.ui_requests import IntUI
from utils.job_pool import JobPool

#===============================================
def terminateAll(sig, frame):
    AnfisaApp.terminate(sig, frame)

#===============================================
class AnfisaApp:
    sConfig = None
    sMongoConn = None
    sVersionCode = None
    sDataVault = None
    sDruidAgent = None
    sRunOptions = None
    sJobPool = None
    sTasks = dict()

    @classmethod
    def setup(cls, config, in_container):
        prepareSolutions()

        with open(os.path.dirname(os.path.abspath(__file__)) +
            "/../VERSION", "r", encoding = "utf-8") as inp:
            cls.sVersionCode = inp.read().strip()

        cls.sConfig = config
        MirrorUiDirectory.setup(cls.sConfig.get("mirror-ui"))
        IntUI.setup(config, in_container)

        cls.sDocReportCSS = MirrorUiDirectory.transform(
            cls.sConfig["doc-report-css"])
        cls.sDocPygmentsCSS = MirrorUiDirectory.transform(
            cls.sConfig["doc-pygments-css"])

        cls.sRunOptions = cls.sConfig.get("run-options")
        if not cls.sRunOptions:
            cls.sRunOptions = []

        cls.sMongoConn = MongoConnector(cls.sConfig["mongo-db"],
            cls.sConfig.get("mongo-host"), cls.sConfig.get("mongo-port"))

        if cls.sConfig.get("link-base") is not None:
            AttrH.setupLinkBase(*cls.sConfig["link-base"])

        cls.sDruidAgent = DruidAgent(cls.sConfig)

        cls.sDataVault = DataVault(cls, cls.sConfig["data-vault"])

        cls.sJobPool = JobPool(
            AnfisaConfig.configOption("job.pool.threads"),
            AnfisaConfig.configOption("job.pool.size"))

        signal.signal(signal.SIGTERM, terminateAll)
        signal.signal(signal.SIGHUP, terminateAll)
        signal.signal(signal.SIGINT, terminateAll)

    @classmethod
    def terminate(cls, sig, frame):
        cls.sMongoConn.close()
        cls.sJobPool.close()
        logging.info("Application terminated")
        sys.exit(0)

    @classmethod
    def makeExcelExport(cls, prefix, ds_h, rec_no_seq, tags_man = None):
        export_setup = cls.sConfig["export"]
        dir_name = export_setup["work-dir"]
        if not os.path.dirname(dir_name):
            return None
        if dir_name.endswith('/'):
            dir_name = dir_name[:-1]
        dir_name += '/'
        for no in range(10000):
            fname = "%s_%04d.xlsx" % (prefix, no)
            #debug_file_name = "%s_%04d.json" % (prefix, no)
            if os.path.exists(dir_name + fname):
                fname = None
            else:
                break
        if fname is None:
            return None
        source_versions = [["version", ds_h.getDataVault().
            getApp().getVersionCode()]] + ds_h.getSourceVersions()
        tags_info = tags_man.getTagListInfo() if tags_man is not None else None

        export_h = ExcelExport(export_setup["excel-template"],
            source_versions = source_versions, tags_info = tags_info)
        #exp_rep = _ExportReport(dir_name + debug_file_name,
        #    source_versions, tags_info)
        for rec_no in rec_no_seq:
            rec_data = ds_h.getRecordData(rec_no)
            tags_data = tags_man.getRecTags(rec_no) if tags_man else None
            export_h.add_variant(rec_data, tags_data)
            #exp_rep.record(rec_data, tags_data)
        export_h.save(dir_name + fname)
        #exp_rep.close()
        return 'excel/' + fname

    @classmethod
    def getVersionCode(cls):
        return cls.sVersionCode

    @classmethod
    def getMongoConnector(cls):
        return cls.sMongoConn

    @classmethod
    def getDataVault(cls):
        return cls.sDataVault

    @classmethod
    def getDruidAgent(cls):
        return cls.sDruidAgent

    @classmethod
    def hasRunOption(cls, name):
        return name in cls.sRunOptions

    @classmethod
    def request(cls, serv_h, rq_path, rq_args, rq_descr):
        func, agent = RestAPI.lookupRequest(
            rq_path, rq_args, cls.sDataVault)
        if func is not None:
            if agent is not None:
                agent.descrContext(rq_args, rq_descr)
            report = func(agent, rq_args)
            return serv_h.makeResponse(mode = "json",
                content = json.dumps(report))

        return IntUI.finishRequest(serv_h,
            rq_path, rq_args, cls.sDataVault)

    @classmethod
    def viewSingleRecord(cls, record, research_mode):
        view_aspects = defineViewSchema()
        view_checker = ViewDataChecker(view_aspects)
        view_checker.regValue(0, record)
        rep_out = StringIO()
        is_ok = view_checker.finishUp(rep_out)
        if not is_ok:
            logging.error("Single record annotation failed:\n" +
                rep_out.getvalue())
        assert is_ok
        aspects = AspectSetH.load(view_aspects.dump())
        return aspects.getViewRepr(record, research_mode)

    @classmethod
    def runTask(cls, task):
        cls.sJobPool.putTask(task)
        return str(task.getUID())

    @classmethod
    def askJobStatus(cls, task_id):
        return cls.sJobPool.askTaskStatus(int(task_id));

    @classmethod
    def checkFilePath(cls, path):
        if not path.startswith("/doc/"):
            return None
        ds_name, _, fpath = path[5:].partition('/')
        loc_path = fpath.rpartition('/')[-1]
        if loc_path == "report.css":
            return cls.sDocReportCSS
        if loc_path == "py_pygments.css":
            return cls.sDocPygmentsCSS
        real_path = cls.sDataVault.getDir() + '/' + ds_name + '/doc/' + fpath
        return real_path

#===============================================
class _ExportReport:
    sActive = True

    def __init__(self, debug_file_path, source_versions, tags_info):
        if not self.sActive:
            self.mOutput = None
            return
        self.mOutput = open(debug_file_path, "w", encoding = "utf-8")
        print("@VERSIONS",file = self.mOutput)
        print(json.dumps(source_versions, ensure_ascii = False),
            file = self.mOutput)
        print("@TAGS_CFG",file = self.mOutput)
        print(json.dumps(tags_info, ensure_ascii = False),
            file = self.mOutput)

    def close(self):
        if self.mOutput is not None:
            self.mOutput.close()
            self.mOutput = None

    def record(self, rec_data, tags_data):
        if self.mOutput is None:
            return
        print("@RECORD",file = self.mOutput)
        print(json.dumps(rec_data, ensure_ascii = False),
            file = self.mOutput)
        print("@TAGS",file = self.mOutput)
        print(json.dumps(tags_data, ensure_ascii = False),
            file = self.mOutput)


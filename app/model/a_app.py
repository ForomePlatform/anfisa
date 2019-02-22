import os, json, codecs, logging
from StringIO import StringIO

from .rest_api import RestAPI
from .mongo_db import MongoConnector
from .data_vault import DataVault
from .druid_agent import DruidAgent
from export.excel import ExcelExport
from app.view.attr import AttrH
from int_ui.mirror_dir import MirrorUiDirectory
from int_ui.ui_requests import IntUI

from app.prepare.view_schema import defineViewSchema
from app.prepare.v_check import ViewDataChecker
from app.view.asp_set import AspectSetH
#===============================================
class AnfisaApp:
    sConfig = None
    sMongoConn = None
    sVersionCode = None
    sDataVault = None
    sDruidAgent = None

    @classmethod
    def setup(cls, config, in_container):
        with codecs.open(os.path.dirname(os.path.abspath(__file__)) +
            "/../VERSION", "r", encoding = "utf-8") as inp:
            cls.sVersionCode = inp.read().strip()

        cls.sConfig = config
        MirrorUiDirectory.setup(cls.sConfig.get("mirror-ui"))
        IntUI.setup(config, in_container)

        cls.sMongoConn = MongoConnector(cls.sConfig["mongo-db"],
            cls.sConfig.get("mongo-host"), cls.sConfig.get("mongo-port"))

        if cls.sConfig.get("link-base") is not None:
            AttrH.setupLinkBase(*cls.sConfig["link-base"])

        cls.sDruidAgent = DruidAgent(cls.sConfig)

        cls.sDataVault = DataVault(cls, cls.sConfig["data-vault"],
            cls.sConfig.get("default-ws"), cls.sConfig.get("default-xl"))

    @classmethod
    def makeExcelExport(cls, prefix, ds_h, rec_no_seq):
        export_setup = cls.sConfig["export"]
        dir_name = export_setup["work-dir"]
        if not os.path.dirname(dir_name):
            return None
        if dir_name.endswith('/'):
            dir_name = dir_name[:-1]
        dir_name += '/'
        for no in range(10000):
            fname = "%s_%04d.xlsx" % (prefix, no)
            if os.path.exists(dir_name + fname):
                fname = None
            else:
                break
        if fname is None:
            return None
        export_h = ExcelExport(export_setup["excel-template"])
        export_h.new()
        for rec_no in rec_no_seq:
            export_h.add_variant(ds_h.getRecordData(rec_no))
        export_h.save(dir_name + fname)
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
    def request(cls, serv_h, rq_path, rq_args):
        func, agent = RestAPI.lookupRequest(
            rq_path, rq_args, cls.sDataVault)
        if func is not None:
            report = func(agent, rq_args)
            return serv_h.makeResponse(mode = "json",
                content = json.dumps(report))

        return IntUI.finishRequest(serv_h, rq_path, rq_args, cls.sDataVault)

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

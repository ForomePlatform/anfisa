import logging, os, codecs
from StringIO import StringIO

from app.model.a_serv import AnfisaService
from app.model.workspace import Workspace
from app.model.mongo_db import MongoConnector
from app.view.dataset import DataSet
from .view_setup import ViewSetup
from .view_cfg import setupRecommended
from .search_setup import prepareLegend
from export.excel import ExcelExport
from app.view.attr import AttrH
from int_ui.mirror_dir import MirrorUiDirectory
from app.xl.xl_dataset import XL_Dataset
#===============================================
class AnfisaData:
    sConfig = None
    sDefaultWS = None
    sService = None
    sWorkspaces = {}
    sWsOrdered = []
    sMongoConn = None
    sVersionCode = None
    sXL_Datasets = {}
    sXlOrdered = []
    sDefaultDS = None

    @classmethod
    def setup(cls, config, in_container):
        cls.sConfig = config
        MirrorUiDirectory.setup(config.get("mirror-ui"))

        cls.sMongoConn = MongoConnector(config["mongo-db"],
            config.get("mongo-host"), config.get("mongo-port"))
        setupRecommended()

        for ws_descr in config["workspaces"]:
            ws_name = ws_descr["name"]
            data_set = DataSet(ViewSetup(), ws_name, ws_descr["file"])
            legend = prepareLegend(ws_name)
            legend.testDataSet(data_set)
            rep_out = StringIO()
            legend.setup(rep_out)
            if not legend.isOK():
                logging.fatal(("FILTER LEGEND for %s FAILED\n" % ws_name) +
                    rep_out.gevalue())
            logging.warning(legend.getStatusInfo())
            ws = Workspace(ws_name, legend, data_set,
               cls.sMongoConn.getAgent(ws_descr["mongo-name"]))
            cls.sWorkspaces[ws_name] = ws
            if cls.sDefaultDS is None:
                cls.sDefaultDS = ws
            cls.sWsOrdered.append(ws)

        if config.get("link-base") is not None:
            AttrH.setupBaseHostReplacement(*config["link-base"])

        if config.get("xl-sets"):
            for descr in config["xl-sets"]:
                xl_ds = XL_Dataset(descr["file"],
                    descr["name"], descr["title"],
                    config["druid"]["url_query"])
                cls.sXL_Datasets[xl_ds.getName()] = xl_ds
                cls.sXlOrdered.append(xl_ds)
                if cls.sDefaultDS is None:
                    cls.sDefaultDS = xl_ds

        cls.sService = AnfisaService.start(cls, config, in_container)
        return cls.sService

    @classmethod
    def getWS(cls, name):
        if not name:
            return cls.sDefaultWS
        return cls.sWorkspaces.get(name)

    @classmethod
    def iterWorkspaces(cls):
        return iter(cls.sWsOrdered)

    @classmethod
    def getDS(cls, name):
        if not name:
            return cls.sDefaultDS
        return cls.sXL_Datasets.get(name)

    @classmethod
    def iterXLDatasets(cls):
        return iter(cls.sXlOrdered)

    @classmethod
    def makeExcelExport(cls, prefix, json_seq):
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
        for obj in json_seq:
            export_h.add_variant(obj)
        export_h.save(dir_name + fname)
        return 'excel/' + fname

    @classmethod
    def getVersionCode(cls):
        if cls.sVersionCode is None:
            with codecs.open(os.path.dirname(os.path.abspath(__file__)) +
                "/VERSION", "r", encoding = "utf-8") as inp:
                cls.sVersionCode = inp.read().strip()
        return cls.sVersionCode

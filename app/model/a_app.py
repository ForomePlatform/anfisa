import os, json, codecs

from .rest_api import RestAPI
from .mongo_db import MongoConnector
from .data_vault import DataVault
from .druid_agent import DruidAgent
from export.excel import ExcelExport
from app.view.attr import AttrH
from int_ui.mirror_dir import MirrorUiDirectory
from int_ui.ui_requests import IntUI
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

#from app.model.a_serv import AnfisaService
#from app.view.dataset import DataSet
#from .view_setup import ViewSetup
#from .view_cfg import setupRecommended
#from .search_setup import prepareLegend
#from app.xl.xl_dataset import XL_Dataset
#
#        for ws_descr in config["workspaces"]:
#            ws_name = ws_descr["name"]
#            data_set = DataSet(ViewSetup(), ws_name, ws_descr["file"])
#            legend = prepareLegend(ws_name)
#            legend.testDataSet(data_set)
#            rep_out = StringIO()
#            legend.setup(rep_out)
#            if not legend.isOK():
#                logging.fatal(("FILTER LEGEND for %s FAILED\n" % ws_name) +
#                    rep_out.gevalue())
#            logging.warning(legend.getStatusInfo())
#            ws = Workspace(ws_name, legend, data_set,
#               cls.sMongoConn.getWSAgent(ws_descr["mongo-name"]))
#            cls.sWorkspaces[ws_name] = ws
#            if cls.sDefaultWS is None:
#                cls.sDefaultWS = ws
#            cls.sWsOrdered.append(ws)
#
#
#        if config.get("xl-sets"):
#            for descr in config["xl-sets"]:
#                xl_ds = XL_Dataset(descr["file"], descr["name"],
#                    config["druid"]["url_query"],
#                    cls.sMongoConn.getDSAgent(descr["mongo-name"]))
#                cls.sXL_Datasets[xl_ds.getName()] = xl_ds
#                cls.sXlOrdered.append(xl_ds)
#                if cls.sDefaultDS is None:
#                    cls.sDefaultDS = xl_ds
#
#        cls.sService = AnfisaService.start(cls, config, in_container)
#        return cls.sService
#
#
#
##@classmethod
#def getWS(cls, name):
#    if not name:
#        return cls.sDefaultWS
#    return cls.sWorkspaces.get(name)
#
##@classmethod
#def iterWorkspaces(cls):
#    return iter(cls.sWsOrdered)
#
##@classmethod
#def getDS(cls, name):
#    if not name:
#        return cls.sDefaultDS
#    return cls.sXL_Datasets.get(name)
#
##@classmethod
#def iterXLDatasets(cls):
#    return iter(cls.sXlOrdered)

import logging
from StringIO import StringIO

from app.model.workspace import Workspace
from app.view.dataset import DataSet
from app.view.checker import ViewDataChecker
from .view_setup import ViewSetup
from .view_cfg import setupRecommended
from .search_setup import MainLegend
from app.model.a_serv import AnfisaService

#===============================================
class AnfisaData:
    sWorkspaces = {}
    sDefaultWS = None
    sService = None

    @classmethod
    def setup(cls, config, in_container):
        setupRecommended()
        ws_seq = []
        for ws_descr in config["workspaces"]:
            ws_name = ws_descr["name"]
            data_set = DataSet(ViewSetup, ws_name, ws_descr["file"])
            ViewDataChecker.check(ViewSetup, data_set)
            MainLegend.testDataSet(data_set)
            ws_seq.append((ws_name, data_set, ws_descr))

        rep_out = StringIO()
        MainLegend.setup(rep_out)
        if not MainLegend.isOK():
            logging.fatal("FILTER LEGEND FAILED\n" + rep_out.gevalue())
        logging.warning(MainLegend.getStatusInfo())

        for ws_name, data_set, ws_descr in ws_seq:
            ws = Workspace(ws_name, MainLegend, data_set,
                ws_descr["mongo"],
                ws_descr.get("mongo-host"), ws_descr.get("mongo-port"))
            cls.sWorkspaces[ws_name] = ws
            if cls.sDefaultWS is None:
                cls.sDefaultWS = ws

        cls.sService = AnfisaService.start(cls, config, in_container)
        return cls.sService

    @classmethod
    def getWS(cls, name):
        if not name:
            return cls.sDefaultWS
        return cls.sWorkspaces[name]

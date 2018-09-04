import logging
from StringIO import StringIO

from .view_setup   import ViewSetup
from .workspace    import Workspace
from .search_setup import MainLegend
from .view_cfg     import setupRecommended
from view.dataset     import DataSet
from view.checker     import ViewDataChecker
#===============================================
class AnfisaData:
    sWorkspaces = {}
    sDefaultWS = None

    @classmethod
    def setup(cls, config):
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

    @classmethod
    def getWS(cls, name):
        if not name:
            return cls.sDefaultWS
        return cls.sWorkspaces[name]


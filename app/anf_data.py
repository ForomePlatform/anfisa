import logging, os
from StringIO import StringIO

from app.model.a_serv import AnfisaService
from app.model.workspace import Workspace
from app.view.dataset import DataSet
from app.view.checker import ViewDataChecker
from .view_setup import ViewSetup
from .view_cfg import setupRecommended
from .search_setup import MainLegend
from export.excel import ExcelExport

#===============================================
class AnfisaData:
    sConfig = None
    sDefaultWS = None
    sService = None
    sWorkspaces = {}

    @classmethod
    def setup(cls, config, in_container):
        cls.sConfig = config
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

    @classmethod
    def makeExcelExport(cls, prefix, json_seq):
        export_setup = cls.sConfig["export"]
        dir_name = export_setup["work-dir"]
        if not os.path.dirname(dir_name):
            return None
        if dir_name.endswith('/'):
            dir_name = dir_name[:-1]
        loc_dir = dir_name.rpartition('/')[2]
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
        return loc_dir + '/' + fname

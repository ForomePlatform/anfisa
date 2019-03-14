from StringIO import StringIO

from .gen_html import formTopPage, noRecords, dirPage, notFound
from .html_xl import formXLPage
from .html_xltree import formXLTreePage
from .record import reportRecord
#===============================================
class IntUI:
    sHtmlBase = None
    sHtmlTitleWS = None
    sHtmlTitleXL = None

    @classmethod
    def setup(cls, config, in_container):
        cls.sHtmlTitleWS = config["html-title-ws"]
        cls.sHtmlTitleXL = config["html-title-xl"]
        cls.sHtmlBase = (config["html-base"]
            if in_container else None)
        if cls.sHtmlBase and not cls.sHtmlBase.endswith('/'):
            cls.sHtmlBase += '/'

    @classmethod
    def notFoundResponse(cls, serv_h):
        output = StringIO()
        notFound(output, cls.sHtmlTitleWS, cls.sHtmlBase)
        return serv_h.makeResponse(content = output.getvalue(),
            error = 404)

    @classmethod
    def finishRequest(cls, serv_h, rq_path, rq_args, data_vault):
        if rq_path == "/" or rq_path == "/ws":
            workspace = data_vault.getWS(rq_args.get("ws"))
            if workspace is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formTopPage(output, cls.sHtmlTitleWS, cls.sHtmlBase,
                workspace)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/rec":
            workspace = data_vault.getWS(rq_args.get("ws"))
            modes = rq_args.get("m", "").upper()
            rec_no = int(rq_args.get("rec"))
            port = rq_args.get("port")
            if workspace:
                output = StringIO()
                reportRecord(output, workspace, 'R' in modes, rec_no, port)
                return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/dir":
            output = StringIO()
            dirPage(output, cls.sHtmlTitleWS, cls.sHtmlBase)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/norecords":
            output = StringIO()
            noRecords(output)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/xl_flt":
            xl_ds = data_vault.getXL(rq_args.get("ds"))
            if xl_ds is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formXLPage(output, cls.sHtmlTitleXL, cls.sHtmlTitleWS,
                cls.sHtmlBase, xl_ds)
            return serv_h.makeResponse(content = output.getvalue())

        if rq_path == "/xl_tree":
            xl_ds = data_vault.getXL(rq_args.get("ds"))
            if xl_ds is None:
                return cls.notFoundResponse(serv_h)
            output = StringIO()
            formXLTreePage(output, cls.sHtmlTitleXL, cls.sHtmlTitleWS,
                cls.sHtmlBase, xl_ds)
            return serv_h.makeResponse(content = output.getvalue())
        return cls.notFoundResponse(serv_h)


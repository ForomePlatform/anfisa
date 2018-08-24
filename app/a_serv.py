# import sys
import json
from StringIO import StringIO
from .anf_data import AnfisaData
from view.gen_html import formTopPage, emptyPage

#===============================================
class HTML_Setup:

    START = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'

    META_UTF = \
        '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'

    STYLE_SHEET_REF = \
        '  <link rel="stylesheet" href="%s" type="text/css" media="all"/>'

    JS_REF = \
        '  <script type="text/javascript" src="%s">\n </script>'

#===============================================
class AnfisaService:
    sMain = None

    @classmethod
    def start(cls, config, in_container):
        assert cls.sMain is None
        cls.sMain = cls(config, in_container)

    @classmethod
    def request(cls, serv_h, rq_path, rq_args):
        if rq_path == "/":
            return serv_h.makeResponse(
                content = cls.sMain.formTop(rq_args))
        if rq_path == "/rec":
            return serv_h.makeResponse(
                content = cls.sMain.formRec(rq_args))
        if rq_path == "/norecords":
            return serv_h.makeResponse(
                content = cls.sMain.formNoRec(rq_args))
        if rq_path == "/list":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formList(rq_args))

        return serv_h.makeResponse(error = 404)

    #===============================================
    def __init__(self, config, in_container):
        self.mConfig = config
        self.mInContainer = in_container
        AnfisaData.setup(config)
        self.mHtmlTitle = self.mConfig["html-title"]
        self.mHtmlBase = (self.mConfig["html-base"]
            if self.mInContainer else None)
        if self.mHtmlBase and not self.mHtmlBase.endswith('/'):
            self.mHtmlBase += '/'

    #===============================================
    def _formHtmlHead(self, output, title = None,
            css_files = None, js_files = None):
        print >> output, '<head>'
        print >> output, HTML_Setup.META_UTF
        if self.mHtmlBase:
            print >> output, ' <base href="%s" />' % self.mHtmlBase
        if css_files:
            for fname in css_files:
                print >> output, HTML_Setup.STYLE_SHEET_REF % fname
        if title:
            print >> output, ' <title>%s</title>' % title
        if js_files:
            for fname in js_files:
                print >> output, HTML_Setup.JS_REF % fname
        print >> output, '</head>'

    #===============================================
    def formTop(self, rq_args):
        data_set = AnfisaData.getSet(rq_args.get("data"))
        output = StringIO()
        formTopPage(output, self.mHtmlTitle, self.mHtmlBase,
            data_set.getName(), AnfisaData.getSetNames())
        return output.getvalue()

    #===============================================
    def formRec(self, rq_args):
        output = StringIO()
        data_set = AnfisaData.getSet(rq_args.get("data"))
        rec_no = int(rq_args.get("rec"))
        record = data_set.getRecord(rec_no)
        print >> output, HTML_Setup.START
        print >> output, '<html>'
        self._formHtmlHead(output,
            css_files = ["a_rec.css"], js_files = ["a_rec.js"])
        print >> output, ('<body onload="init_r(\'%s\');">' %
            data_set.getFirstAspectID())
        record.reportIt(output, AnfisaData.getRecHotData(
            data_set.getName(), rec_no))
        print >> output, '</body>'
        print >> output, '</html>'
        return output.getvalue()

    #===============================================
    def formNoRec(self, rq_args):
        output = StringIO()
        emptyPage(output)
        return output.getvalue()

    #===============================================
    def formList(self, rq_args):
        output = StringIO()
        data_index = AnfisaData.getIndex(rq_args.get("data"))
        filter = json.loads(rq_args.get("filter"))
        output.write(json.dumps(data_index.makeJSonReport(filter)))
        return output.getvalue()

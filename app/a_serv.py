#import sys
from StringIO import StringIO
from anf_data import AnfisaData
#===============================================
class HTML_Setup:

    START = '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">'

    META_UTF = \
        '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'

    STYLE_SHEET = \
        '<link rel="stylesheet" href="anf.css" type="text/css" media="all"/>'

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
    def _formHtmlHead(self, output, title = None, js_file = None):
        print >> output, '<head>'
        print >> output, HTML_Setup.META_UTF
        if self.mHtmlBase:
             print >> output, ' <base href="%s" />' % self.mHtmlBase
        print >> output, HTML_Setup.STYLE_SHEET
        if title:
            print >> output, ' <title>%s</title>' % title
        if js_file:
            print >> output, (
                '   <script type="text/javascript" src="%s">' % js_file)
            print >> output, '   </script>'
        print >> output, '</head>'

    #===============================================
    def formTop(self, rq_args):
        data_set = AnfisaData.getSet(rq_args.get("data"))
        output = StringIO()
        print >> output, HTML_Setup.START
        print >> output, '<html>'
        self._formHtmlHead(output,
            title = self.mHtmlTitle % data_set.getName(), js_file = "anf.js")
        print >> output, (
            '<body onload="initWin(\'%s\');">' %
            data_set.getName())
        print >> output, ' <div id="modal-back">'
        print >> output, '   <div id="filter-mod">'
        print >> output, '     <span id="close-filter" ' + \
            'onclick="filterModOff();">&times;</span>'
        print >> output, '     <h3>Filter...</h3>'
        print >> output, '   </div>'
        print >> output, ' </div>'
        print >> output, ' <div id="top">'
        print >> output, '  <div id="top-left">'
        print >> output, '   <div class="data-sets">'
        print >> output, '   <button id="open-filter" ' + \
            'onclick="filterModOn();">Filter</button>'
        AnfisaData.reportSets(data_set, output)
        print >> output, '   </div>'
        print >> output, '   <div class="rec-list">'
        data_set.reportList(output)
        print >> output, '   </div>'
        print >> output, '  </div>'
        print >> output, '  <div id="top-right">'
        print >> output, '   <iframe id="record">'
        print >> output, '   </iframe>'
        print >> output, '  </div>'
        print >> output, ' </div>'
        print >> output, '</body>'
        print >> output, '</html>'
        return output.getvalue()

    #===============================================
    def formRec(self, rq_args):
        output = StringIO()
        data_set = AnfisaData.getSet(rq_args.get("data"))
        record = data_set.getRecord(rq_args.get("rec"))
        print >> output, HTML_Setup.START
        print >> output, '<html>'
        self._formHtmlHead(output, js_file = "a_rec.js")
        print >> output, ('<body onload="init_r(\'%s\');" class="rec">' %
            data_set.getFirstAspectID())
        record.reportIt(output)
        print >> output, '</body>'
        print >> output, '</html>'
        return output.getvalue()

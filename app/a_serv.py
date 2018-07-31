#import sys
from StringIO import StringIO
from anf_data import AnfisaData
#===============================================
class HTML_Setup:

    START = '''<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>'''

    META_UTF = \
        '<meta http-equiv="content-type" content="text/html; charset=UTF-8">'

    STYLE_SHEET = \
        '<link rel="stylesheet" href="/anf.css" type="text/css" media="all"/>'

    @staticmethod
    def printRefJS(output, fname):
        print >> output, ('   <script type="text/javascript" src="/%s">' %
            fname)
        print >> output, '   </script>'

#===============================================
class AnfisaService:
    sMain = None
    @classmethod
    def start(cls, config):
        assert cls.sMain is None
        cls.sMain = cls(config)

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
    def __init__(self, config):
        self.mConfig = config
        AnfisaData.setup(config)

    #===============================================
    def formTop(self, rq_args):
        data_set = AnfisaData.getSet(rq_args.get("data"))
        output = StringIO()
        print >> output, HTML_Setup.START
        print >> output, '<html>'
        print >> output, '<head>'
        print >> output, HTML_Setup.META_UTF
        print >> output, HTML_Setup.STYLE_SHEET
        print >> output, ' <title>Anfisa: %s</title>' % data_set.getName()
        HTML_Setup.printRefJS(output, "anf.js")
        print >> output, '</head>'
        print >> output, ('<body onload="changeRec(\'%s\', \'%s\');">' %
            (data_set.getName(), data_set.getRecId(0)))
        print >> output, ' <table class="top"><tr>'
        print >> output, '  <td class="top-left">'
        print >> output, '   <div class="data-sets">'
        AnfisaData.reportSets(data_set, output)
        print >> output, '   </div>'
        print >> output, '   <div class="rec-list">'
        data_set.reportList(output)
        print >> output, '   </div>'
        print >> output, '  </td><td class="top-right">'
        print >> output, '   <iframe id="record">'
        print >> output, '   </iframe>'
        print >> output, '  </td>'
        print >> output, ' </tr></table>'
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
        print >> output, '<head>'
        print >> output, HTML_Setup.META_UTF
        print >> output, HTML_Setup.STYLE_SHEET
        HTML_Setup.printRefJS(output, "a_rec.js")
        print >> output, '</head>'
        print >> output, '<body onload="init_r();" class="rec">'
        record.reportIt(output)
        print >> output, '</body>'
        print >> output, '</html>'
        return output.getvalue()

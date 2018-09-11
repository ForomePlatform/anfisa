# import sys
import json
from StringIO import StringIO
from .anf_data import AnfisaData
from view.gen_html import formTopPage, noRecords

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
                content = cls.sMain.formNoRecords(rq_args))
        if rq_path == "/list":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formList(rq_args))
        if rq_path == "/stat":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formStat(rq_args))
        if rq_path == "/tags":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formTags(rq_args))
        if rq_path == "/zone_list":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formZoneList(rq_args))
        if rq_path == "/rules_data":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formRulesData(rq_args))
        if rq_path == "/rules_modify":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formRulesModify(rq_args))
        if rq_path == "/tag_select":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formTagSelect(rq_args))
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
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        output = StringIO()
        formTopPage(output, self.mHtmlTitle, self.mHtmlBase,
            workspace.getName(), modes, workspace.iterZones())
        return output.getvalue()

    #===============================================
    def formRec(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        data_set = workspace.getDataSet()
        modes = rq_args.get("m", "")
        rec_no = int(rq_args.get("rec"))
        record = data_set.getRecord(rec_no)
        port = rq_args.get("port")
        print >> output, HTML_Setup.START
        print >> output, '<html>'
        self._formHtmlHead(output,
            css_files = ["base.css", "a_rec.css", "tags.css"],
            js_files = ["a_rec.js", "tags.js"])
        if port == "2":
            print >> output, ('<body onload="init_r(2, \'%s\');">' %
                workspace.getFirstAspectID())
        elif port == "1":
            print >> output, ('<body onload="init_r(1, \'%s\');">' %
                workspace.getLastAspectID())
        else:
            print >> output, (
                '<body onload="init_r(0, \'%s\', \'%s\', %d);">' %
                (workspace.getFirstAspectID(), workspace.getName(), rec_no))

        record.reportIt(output, "X" in modes)
        print >> output, '</body>'
        print >> output, '</html>'
        return output.getvalue()

    #===============================================
    def formNoRecords(self, rq_args):
        output = StringIO()
        noRecords(output)
        return output.getvalue()

    #===============================================
    def formList(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        rec_no_seq = workspace.getIndex().getRecNoSeq(
            rq_args.get("filter"))
        zone_data = rq_args.get("zone")
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            rec_no_seq = workspace.getZone(zone_name).restrict(
                rec_no_seq, variants);
        report = workspace.mDataSet.makeJSonReport(
            sorted(rec_no_seq), 'R' in modes,
            workspace.getTagsMan().getMarkedSet())
        report["workspace"] = workspace.getName();
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formStat(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        filter_name = rq_args.get("filter")
        conditions = rq_args.get("conditions")
        if conditions:
            conditions = json.loads(conditions)
        instr = rq_args.get("instr")
        report = workspace.makeStatReport(filter_name,
            'X' in modes, conditions, instr)
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formTags(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        rec_no = int(rq_args.get("rec"))
        tags_to_update = rq_args.get("tags")
        if tags_to_update is not None:
            tags_to_update = json.loads(tags_to_update)
        report = workspace.makeTagsJSonReport(rec_no,
            'X' in modes, tags_to_update)
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formZoneList(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        report = workspace.getZone(rq_args.get("zone")).makeValuesReport()
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formRulesData(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        output.write(json.dumps(
            workspace.getRulesData('X' in modes)))
        return output.getvalue()

    #===============================================
    def formRulesModify(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "")
        item = rq_args.get("it")
        content = rq_args.get("cnt")
        output.write(json.dumps(workspace.modifyRulesData(
            'X' in modes, item, content)))
        return output.getvalue()

    #===============================================
    def formTagSelect(self, rq_args):
        output = StringIO()
        workspace = AnfisaData.getWS(rq_args.get("ws"))
        tags_man = workspace.getTagsMan();
        tag_list = tags_man.getTagList();
        tag_name = rq_args.get("tag")
        if tag_name and tag_name not in tag_list:
            tag_name = None
        rep = {"tag-list": tag_list, "tag": tag_name,
            "tags-version": tags_man.getIntVersion()}
        if tag_name:
            rep["records"] = tags_man.getTagRecordList(
                tag_name)
        output.write(json.dumps(rep))
        return output.getvalue()

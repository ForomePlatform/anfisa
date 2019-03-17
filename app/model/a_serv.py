import json
from StringIO import StringIO

from int_ui.gen_html import formTopPage, noRecords, dirPage, notFound
from int_ui.record import reportRecord
#===============================================
class AnfisaService:
    sData = None
    sMain = None

    @classmethod
    def start(cls, a_data, config, in_container):
        assert cls.sMain is None
        cls.sData = a_data
        cls.sMain = cls(config, in_container)
        return cls.sMain

    @classmethod
    def request(cls, serv_h, rq_path, rq_args):
        if rq_path == "/" or rq_path == "/ws":
            content, error = cls.sMain.formTop(rq_args)
            return serv_h.makeResponse(content = content, error = error)
        if rq_path == "/rec":
            return serv_h.makeResponse(
                content = cls.sMain.formRec(rq_args))
        if rq_path == "/dir":
            return serv_h.makeResponse(
                content = cls.sMain.formDir(rq_args))
        if rq_path == "/norecords":
            return serv_h.makeResponse(
                content = cls.sMain.formNoRecords(rq_args))
        if rq_path == "/list":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formList(rq_args))
        if rq_path == "/dirinfo":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formDirInfo(rq_args))
        if rq_path == "/vsetup":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formVSetup(rq_args))
        if rq_path == "/recdata":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formRecData(rq_args))
        if rq_path == "/reccnt":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formRecContent(rq_args))
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
        if rq_path == "/export":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formExport(rq_args))
        if rq_path == "/wsnote":
            return serv_h.makeResponse(mode = "json",
                content = cls.sMain.formWSNote(rq_args))
        return serv_h.makeResponse(error = 404)

    #===============================================
    def __init__(self, config, in_container):
        self.mConfig = config
        self.mInContainer = in_container
        self.mHtmlTitle = self.mConfig["html-title"]
        self.mHtmlBase = (self.mConfig["html-base"]
            if self.mInContainer else None)
        if self.mHtmlBase and not self.mHtmlBase.endswith('/'):
            self.mHtmlBase += '/'

    #===============================================
    @classmethod
    def _stdParams(cls, rq_args):
        workspace = cls.sData.getWS(rq_args.get("ws"))
        modes = rq_args.get("m", "").upper()
        return workspace, modes

    #===============================================
    # Internal UI methods
    #===============================================
    def formTop(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        output = StringIO()
        err_code = None
        if workspace is not None:
            formTopPage(output, self.mHtmlTitle, self.mHtmlBase,
                workspace)
        else:
            err_code = 404
            notFound(output, self.mHtmlTitle, self.mHtmlBase)
        return output.getvalue(), err_code

    #===============================================
    def formDir(self, rq_args):
        output = StringIO()
        dirPage(output, self.mHtmlTitle, self.mHtmlBase)
        return output.getvalue()

    #===============================================
    def formRec(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        rec_no = int(rq_args.get("rec"))
        port = rq_args.get("port")
        output = StringIO()
        reportRecord(output, workspace, 'R' in modes, rec_no, port)
        return output.getvalue()

    #===============================================
    def formNoRecords(self, rq_args):
        output = StringIO()
        noRecords(output)
        return output.getvalue()

    #===============================================
    # REST methods
    #===============================================
    def formList(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        conditions = rq_args.get("conditions")
        if conditions:
            conditions = json.loads(conditions)
        rec_no_seq = workspace.getIndex().getRecNoSeq(
            rq_args.get("filter"), conditions)
        zone_data = rq_args.get("zone")
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            rec_no_seq = workspace.getZone(zone_name).restrict(
                rec_no_seq, variants)
        report = workspace.mDataSet.makeJSonReport(
            sorted(rec_no_seq), 'S' in modes,
            workspace.getTagsMan().getMarkedSet())
        report["workspace"] = workspace.getName()
        output = StringIO()
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formStat(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        filter_name = rq_args.get("filter")
        conditions = rq_args.get("conditions")
        if conditions:
            conditions = json.loads(conditions)
        instr = rq_args.get("instr")
        report = workspace.makeStatReport(filter_name,
            'R' in modes, conditions, instr)
        output = StringIO()
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formTags(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        rec_no = int(rq_args.get("rec"))
        tags_to_update = rq_args.get("tags")
        if tags_to_update is not None:
            tags_to_update = json.loads(tags_to_update)
        report = workspace.makeTagsJSonReport(rec_no,
            'R' in modes, tags_to_update)
        output = StringIO()
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formZoneList(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        zone = rq_args.get("zone")
        if zone is not None:
            report = workspace.getZone(zone).makeValuesReport()
        else:
            report = [[zone_h.getName(), zone_h.getTitle()]
                for zone_h in workspace.iterZones()]
        output = StringIO()
        output.write(json.dumps(report))
        return output.getvalue()

    #===============================================
    def formRulesData(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        output = StringIO()
        output.write(json.dumps(
            workspace.getRulesData('R' in modes)))
        return output.getvalue()

    #===============================================
    def formRulesModify(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        item = rq_args.get("it")
        content = rq_args.get("cnt")
        output = StringIO()
        output.write(json.dumps(workspace.modifyRulesData(
            'R' in modes, item, content)))
        return output.getvalue()

    #===============================================
    def formTagSelect(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        tags_man = workspace.getTagsMan()
        tag_list = tags_man.getTagList();
        tag_name = rq_args.get("tag")
        if tag_name and tag_name not in tag_list:
            tag_name = None
        rep = {"tag-list": tag_list, "tag": tag_name,
            "tags-version": tags_man.getIntVersion()}
        if tag_name:
            rep["records"] = tags_man.getTagRecordList(
                tag_name)
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

    #===============================================
    def formExport(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        conditions = rq_args.get("conditions")
        if conditions:
            conditions = json.loads(conditions)
        rec_no_seq = workspace.getIndex().getRecNoSeq(
            rq_args.get("filter"), conditions)
        zone_data = rq_args.get("zone")
        if zone_data is not None:
            zone_name, variants = json.loads(zone_data)
            rec_no_seq = workspace.getZone(zone_name).restrict(
                rec_no_seq, variants)
        
        fname = self.sData.makeExcelExport(workspace, rec_no_seq)
        rep = {"kind": "excel", "fname": fname}
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

    #===============================================
    def formVSetup(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        rep = workspace.getDataSet().getViewSetupJSon()
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

    #===============================================
    def formRecData(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        rec_no = int(rq_args.get("rec"))
        rep = workspace.getDataSet().getRecData(rec_no)
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

    #===============================================
    def formRecContent(self, rq_args):
        workspace, modes = self._stdParams(rq_args)
        rec_no = int(rq_args.get("rec"))
        output = StringIO()
        output.write(json.dumps(workspace.getDataSet().getJSonRecRepr(
            rec_no, 'R' in modes)))
        return output.getvalue()

    #===============================================
    def formDirInfo(self, rq_args):
        rep = {
            "version": self.sData.getVersionCode(),
            "workspaces": [workspace.getJSonObj()
                for workspace in self.sData.iterWorkspaces()]}
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

    #===============================================
    def formWSNote(self, rq_args):
        workspace = self.sData.getWS(rq_args.get("ws"))
        note = workspace.getWSNote(rq_args.get("note"))
        rep = {
            "workspace": workspace.getName(),
            "note": note}
        output = StringIO()
        output.write(json.dumps(rep))
        return output.getvalue()

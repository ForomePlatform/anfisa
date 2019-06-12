from xml.sax.saxutils import escape
from app.config.a_config import AnfisaConfig
from .gen_html import tagsBlock, startHtmlPage
#===============================================
def reportWsRecord(output, workspace, research_mode, rec_no, port):
    startHtmlPage(output,
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
    print >> output, '<div class="r-tab">'
    print >> output, ('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>')
    asp_data_seq = workspace.getViewRepr(rec_no, research_mode)
    for asp_data in asp_data_seq:
        print >> output, ('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (asp_data["kind"], asp_data["name"], asp_data["name"],
            AnfisaConfig.decorText(asp_data["title"])))
    tags_asp_name = AnfisaConfig.configOption("aspect.tags.name")
    print >> output, ('<button class="r-tablnk %s" id="la--%s" '
        'onclick="pickAspect(\'%s\')">%s</button>' %
        ("tech",  tags_asp_name, tags_asp_name,
        AnfisaConfig.textMessage("aspect.tags.title")))
    print >> output, '</div>'

    print >> output, '<div id="r-cnt-container">'
    for asp_data in asp_data_seq:
        print >> output, ('<div id="a--%s" class="r-tabcnt">' %
            asp_data["name"])
        _reportAspect(output, asp_data)
        print >> output, '</div>'
    print >> output, ('<div id="a--%s" class="r-tabcnt">' %
        tags_asp_name)
    tagsBlock(output)
    print >> output, '</div>'

    print >> output, '</div>'
    print >> output, '</body>'
    print >> output, '</html>'

#===============================================
def reportXlRecord(output, dataset, rec_no):
    startHtmlPage(output,
        css_files = ["base.css", "a_rec.css"],
        js_files = ["xl_rec.js"])
    print >> output, (
        '<body onload="init_r(\'%s\', \'%s\', %d);">' %
        (dataset.getFirstAspectID(), dataset.getName(), rec_no))
    print >> output, '<div class="r-tab">'
    print >> output, ('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>')
    asp_data_seq = dataset.getViewRepr(rec_no, True)
    for asp_data in asp_data_seq:
        print >> output, ('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (asp_data["kind"], asp_data["name"], asp_data["name"],
            AnfisaConfig.decorText(asp_data["title"])))
    print >> output, '</div>'

    print >> output, '<div id="r-cnt-container">'
    for asp_data in asp_data_seq:
        print >> output, ('<div id="a--%s" class="r-tabcnt">' %
            asp_data["name"])
        _reportAspect(output, asp_data)
        print >> output, '</div>'
    print >> output, '</div>'

    print >> output, '</div>'
    print >> output, '</body>'
    print >> output, '</html>'

#===============================================
def _reportAspect(output, rep_data):
    if rep_data["type"] == "table":
        n_col = rep_data["columns"]
        print >> output, '<table id="rec-%s">' % rep_data["name"]
        if rep_data.get("colhead"):
            print >> output, '<tr class="head"><td class="title"></td>'
            for title, count in rep_data["colhead"]:
                print >> output, ('<td class="title" colspan="%d">%s</td>' %
                (count, title))
        print >> output, '</tr>'

        for attr_data in rep_data["rows"]:
            if len(attr_data) == 0:
                print >> output, (
                    '<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                    (n_col + 1))
                continue
            print >> output, '<tr>'
            if len(attr_data) > 3:
                print >> output, '<td class="title" title="%s">%s</td>' % (
                    escape(attr_data[3]), attr_data[1])
            else:
                print >> output, '<td class="title">%s</td>' % attr_data[1]
            for val, class_name in attr_data[2]:
                print >> output, '<td class="%s">%s</td>' % (class_name, val)
            print >> output, '</tr>'
        print >> output, '</table>'
    else:
        assert rep_data["type"] == "pre"
        if "content" in rep_data:
            print >> output, '<pre>'
            print >> output, rep_data["content"]
            print >> output, '</pre>'
        else:
            print >> output, '<p class="error">No input data</p>'

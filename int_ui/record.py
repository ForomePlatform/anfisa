from xml.sax.saxutils import escape
from app.config.a_config import AnfisaConfig
from .gen_html import tagsBlock, startHtmlPage
#===============================================
def reportWsRecord(output, workspace, research_mode, rec_no, port):
    startHtmlPage(output,
        css_files = ["base.css", "a_rec.css", "tags.css"],
        js_files = ["a_rec.js", "tags.js", "base.js"])
    if port == "2":
        print('<body onload="init_r(2, \'%s\');">' %
            workspace.getFirstAspectID(), file = output)
    elif port == "1":
        print('<body onload="init_r(1, \'%s\');">' %
            workspace.getLastAspectID(), file = output)
    else:
        print('<body onload="init_r(0, \'%s\', \'%s\', %d);">' %
            (workspace.getFirstAspectID(), workspace.getName(), rec_no),
            file = output)
    print('<div class="r-tab">', file = output)
    print('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>',
        file = output)
    asp_data_seq = workspace.getViewRepr(rec_no, research_mode)
    for asp_data in asp_data_seq:
        print('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (asp_data["kind"], asp_data["name"], asp_data["name"],
            AnfisaConfig.decorText(asp_data["title"])), file = output)
    tags_asp_name = AnfisaConfig.configOption("aspect.tags.name")
    print('<button class="r-tablnk %s" id="la--%s" '
        'onclick="pickAspect(\'%s\')">%s</button>' %
        ("tech",  tags_asp_name, tags_asp_name,
        AnfisaConfig.textMessage("aspect.tags.title")), file = output)
    print('</div>', file = output)

    print('<div id="r-cnt-container">', file = output)
    for asp_data in asp_data_seq:
        print('<div id="a--%s" class="r-tabcnt">' %
            asp_data["name"], file = output)
        _reportAspect(output, asp_data)
        print('</div>', file = output)
    print(('<div id="a--%s" class="r-tabcnt">' % tags_asp_name), file = output)
    tagsBlock(output)
    print('</div>', file = output)

    print('</div>', file = output)
    print('</body>', file = output)
    print('</html>', file = output)

#===============================================
def reportXlRecord(output, dataset, rec_no):
    startHtmlPage(output,
        css_files = ["base.css", "a_rec.css"],
        js_files = ["xl_rec.js"])
    print('<body onload="init_r(\'%s\', \'%s\', %d);">' %
        (dataset.getFirstAspectID(), dataset.getName(), rec_no), file = output)
    print('<div class="r-tab">', file = output)
    print('<span id="img-wrap" onclick="tabCfgChange();">'
        '<img id="img-tab2" src="ui/images/tab2-exp.png"/></span>',
        file = output)
    asp_data_seq = dataset.getViewRepr(rec_no, True)
    for asp_data in asp_data_seq:
        print('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (asp_data["kind"], asp_data["name"], asp_data["name"],
            AnfisaConfig.decorText(asp_data["title"])), file = output)
    print('</div>', file = output)

    print('<div id="r-cnt-container">', file = output)
    for asp_data in asp_data_seq:
        print('<div id="a--%s" class="r-tabcnt">' %
            asp_data["name"], file = output)
        _reportAspect(output, asp_data)
        print('</div>', file = output)
    print('</div>', file = output)

    print('</div>', file = output)
    print('</body>', file = output)
    print('</html>', file = output)

#===============================================
def _reportAspect(output, rep_data):
    if rep_data["type"] == "table":
        n_col = rep_data["columns"]
        print('<table id="rec-%s">' % rep_data["name"], file = output)
        if rep_data.get("colhead"):
            print('<tr class="head"><td class="title"></td>', file = output)
            for title, count in rep_data["colhead"]:
                print('<td class="title" colspan="%d">%s</td>' %
                (count, title), file = output)
        print('</tr>', file = output)

        for attr_data in rep_data["rows"]:
            if len(attr_data) == 0:
                print('<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                    (n_col + 1), file = output)
                continue
            print('<tr>', file = output)
            if len(attr_data) > 3:
                print('<td class="title" title="%s">%s</td>' % (
                    escape(attr_data[3]), attr_data[1]), file = output)
            else:
                print('<td class="title">%s</td>' % attr_data[1],
                    file = output)
            for val, class_name in attr_data[2]:
                print('<td class="%s">%s</td>' % (class_name, val),
                    file = output)
            print('</tr>', file = output)
        print('</table>', file = output)
    else:
        assert rep_data["type"] == "pre"
        if "content" in rep_data:
            print('<pre>', file = output)
            print(rep_data["content"], file = output)
            print('</pre>', file = output)
        else:
            print('<p class="error">No input data</p>', file = output)

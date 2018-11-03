from xml.sax.saxutils import escape

from .gen_html import tagsBlock, startHtmlPage
from .attr_repr import attrHtmlRepr

#===============================================
def reportRecord(output, workspace, research_mode, rec_no, port):
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
        '<img id="img-tab2" src="images/tab2-exp.png"/></span>')
    view_setup = workspace.getDataSet().getViewSetup()
    aspects_to_show = []
    for aspect in view_setup.iterAspects():
        if aspect.isIgnored():
            continue
        if aspect.checkResearchBlock(research_mode):
            continue
        aspects_to_show.append(aspect)
        print >> output, ('<button class="r-tablnk %s" id="la--%s" '
            'onclick="pickAspect(\'%s\')">%s</button>' %
            (aspect.getAspectKind(), aspect.getName(),
            aspect.getName(), aspect.getTitle()))
    tags_asp_name = view_setup.configOption("aspect.tags.name")
    print >> output, ('<button class="r-tablnk %s" id="la--%s" '
        'onclick="pickAspect(\'%s\')">%s</button>' %
        ("tech",  tags_asp_name, tags_asp_name,
        view_setup.textMessage("aspect.tags.title")))
    print >> output, '</div>'

    rec_data = workspace.getDataSet().getRecData(rec_no)
    print >> output, '<div id="r-cnt-container">'
    for asp_h in aspects_to_show:
        print >> output, ('<div id="a--%s" class="r-tabcnt">' %
            asp_h.getName())
        if asp_h.getName() == "input":
            _reportInput(output, rec_data)
        else:
            _reportAspect(output, asp_h, rec_data, research_mode)
        print >> output, '</div>'
    print >> output, ('<div id="a--%s" class="r-tabcnt">' %
        tags_asp_name)
    tagsBlock(output)
    print >> output, '</div>'

    print >> output, '</div>'
    print >> output, '</body>'
    print >> output, '</html>'

#===============================================
def _reportAspect(output, asp_h, rec_obj, research_mode):
    objects = [rec_obj[asp_h.getSource()]]
    if asp_h.getField():
        objects = [objects[0][asp_h.getField()]]
    prefix_head = None
    if asp_h.getColGroups():
        objects, prefix_head = asp_h.getColGroups().prepareObjects(objects)
    if len(objects) == 0:
        return
    fld_data = dict()
    for attr in asp_h.getAttrs():
        if (attr.getName() is None or
                attr.checkResearchBlock(research_mode) or
                attr.hasKind("hidden")):
            continue
        values = [attrHtmlRepr(attr, obj) for obj in objects]
        if not all([vv == ('-', "none") for vv in values]):
            fld_data[attr.getName()] = values

    print >> output, '<table id="rec-%s">' % asp_h.getName()
    if prefix_head:
        print >> output, '<tr class="head"><td class="title"></td>'
        for title, count in prefix_head:
            print >> output, ('<td class="title" colspan="%d">%s</td>' %
                (count, escape(title)))
        print >> output, '</tr>'

    for attr in asp_h.getAttrs():
        if attr.getName() is None:
            print >> output, (
                '<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                (len(objects) + 1))
            continue
        if attr.getName() not in fld_data:
            continue
        print >> output, '<tr>'
        print >> output, '<td class="title">%s</td>' % escape(
            attr.getTitle())
        for val, class_name in fld_data[attr.getName()]:
            print >> output, '<td class="%s">%s</td>' % (class_name, val)
        print >> output, '</tr>'
    print >> output, '</table>'

#===============================================
def _reportInput(output, rec_data):
    if "input" not in rec_data["data"]:
        print >> output, '<p class="error">No input data</p>'
        return
    print >> output, '<pre>'
    collect_str = ""
    for fld in rec_data["data"]["input"].split('\t'):
        if len(fld) < 40:
            if len(collect_str) < 60:
                collect_str += "\t" + fld
            else:
                print >> output, collect_str[1:]
                collect_str = "\t" + fld
            continue
        if collect_str:
            print >> output, collect_str[1:]
            collect_str = ""
        for vv in fld.split(';'):
            var, q, val = vv.partition('=')
            if var == "CSQ":
                print >> output, "==v====SCQ======v========"
                for idx, dt in enumerate(val.split(',')):
                    ddd = dt.split('|')
                    print >> output, "%d:\t%s" % (idx, '|'.join(ddd[:12]))
                    print >> output, "\t|%s" % ('|'.join(ddd[12:29]))
                    print >> output, "\t|%s" % ('|'.join(ddd[28:33]))
                    print >> output, "\t|%s" % ('|'.join(ddd[33:40]))
                    print >> output, "\t|%s" % ('|'.join(ddd[40:50]))
                    print >> output, "\t|%s" % ('|'.join(ddd[50:]))
                print >> output, "==^====SCQ======^========"
            else:
                print >> output, vv
    if collect_str:
        print >> output, collect_str[1:]
        collect_str = ""

#import sys
from xml.sax.saxutils import escape
#===============================================
def _escapeValue(val):
    if isinstance(val, list):
        return ", ".join([_escapeValue(v) for v in val])
    return escape(str(val).replace('_', ' '))

def formAspectTable(output, aspect, rec_obj):
    if aspect.getColGroups():
        prefix_head = []
        objects = []
        for grp in aspect.getColGroups():
            if grp.getAttr() not in rec_obj:
                continue
            seq = rec_obj[grp.getAttr()]
            if len(seq) == 0:
                continue
            objects += seq
            prefix_head.append((grp.getTitle(), len(seq)))
        if len(prefix_head) == 1 and prefix_head[0][0] is None:
            prefix_head = None
        if len(objects) == 0:
            return
    else:
        prefix_head = None
        if aspect.getJsonContainer():
            if aspect.getJsonContainer() not in rec_obj:
                return
            objects = [rec_obj[aspect.getJsonContainer()]]
        else:
            objects = [rec_obj]
    assert objects

    fld_data = dict()
    n_obj = len(objects)
    for attr in aspect.getAttrs():
        if attr.getName() is None:
            continue
        if attr.getKind() == "hidden":
            continue
        values = [attr.getHtmlRepr(obj) for obj in objects]
        if not all([vv == ('-', "none") for vv in values]):
            fld_data[attr.getName()] = values

    print >> output, '<table id="rec-%s">' % aspect.getName()
    if prefix_head:
        print >> output, '<tr class="head"><td class="title"></td>'
        for title, count in prefix_head:
            print >> output, ('<td class="title" colspan="%d">%s</td>' %
                (count, escape(title)))
        print >> output, '</tr>'

    for attr in aspect.getAttrs():
        if attr.getName() is None:
            print >> output, (
                '<tr><td colspan="%d" class="title">&emsp;</td></tr>' %
                (n_obj + 1))
            continue
        if attr.getName() not in fld_data:
            continue
        print >> output, '<tr>'
        print >> output, '<td class="title">%s</td>' % escape(attr.getTitle())
        for val, class_name in fld_data[attr.getName()]:
            print >> output, '<td class="%s">%s</td>' % (class_name, val)
        print >> output, '</tr>'
    print >> output, '</table>'

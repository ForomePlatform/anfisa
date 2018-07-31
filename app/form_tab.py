#import sys
from xml.sax.saxutils import escape
#===============================================
def _escapeValue(val):
    if isinstance(val, list):
        return ", ".join([_escapeValue(v) for v in val])
    return escape(str(val).replace('_', ' '))

def formTable(output, table_id, objects, fields, options,
        use_fields = None, prefix_head = None):
    fld_data = dict()
    n_obj = len(objects)
    for fld in fields:
        if isinstance(fld, list):
            fld, r_fields = fld
            if use_fields is not None:
                for f in r_fields:
                    use_fields[f] = True
            q_found = False
            for f in r_fields:
                if any([f in obj for obj in objects]):
                    q_found = True
                    break
            if not q_found:
                continue
            values = []
            for obj in objects:
                vv = []
                for f in r_fields:
                    if f in obj:
                        vv.append(str(obj[f]))
                if len(vv) > 0:
                    values.append(' '.join(vv))
                else:
                    values.append(None)
        else:
            if use_fields is not None:
                use_fields[fld] = True
            if not any([fld in obj for obj in objects]):
                continue
            values = [obj.get(fld) for obj in objects]
        opts = options.get(fld, {})
        fld_data[fld] = (opts.get("title", fld.replace('_', ' ')),
            opts.get("class"), values)

    print >> output, '<table id="%s">' % table_id
    if prefix_head:
        print >> output, '<tr><td class="title"></td>'
        for title, count in prefix_head:
            print >> output, ('<td class="title" colspan="%d">%s</td>' %
                (count, title))
        print >> output, '</tr>'

    for fld in fields:
        if not fld:
            print >> output, (
                '<tr><td colspan="%d" class="title">.</td></tr>' % (n_obj + 1))
            continue
        if isinstance(fld, list):
            fld = fld[0]
        if fld not in fld_data:
            continue
        title, class_name, values = fld_data[fld]
        print >> output, '<tr>'
        print >> output, '<td class="title">%s</td>' % escape(title)
        if not class_name:
            class_name = "norm"
        for val in values:
            if val:
                vv, cls_name = _escapeValue(val), class_name
            else:
                vv, cls_name = "-", 'none'
            print >> output, '<td class="%s">%s</td>' % (cls_name, vv)
        print >> output, '</tr>'
    print >> output, '</table>'

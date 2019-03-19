import numbers
from StringIO import StringIO
from xml.sax.saxutils import escape

#===============================================
def htmlEscape(val):
    if val is None:
        return "null"
    if val == "":
        return ""
    return escape(unicode(val))

#===============================================
def jsonHtmlRepr(obj, level = 0):
    if obj is None:
        return "null"
    if isinstance(obj, basestring):
        return htmlEscape(obj)
    if isinstance(obj, numbers.Number):
        return str(obj)
    if isinstance(obj, dict):
        if level < 2:
            ret = []
            for key in sorted(obj.keys()):
                if level == 0:
                    ret.append("<b>%s</b>: " % htmlEscape(key))
                    ret.append("<br/>")
                else:
                    ret.append("%s: " % htmlEscape(key))
                rep_val = jsonHtmlRepr(obj[key], level + 1)
                if level == 0:
                    rep_val = htmlEscape(rep_val)
                ret.append(rep_val)
                ret.append(", ")
                if level == 0:
                    ret.append("<br/>")
            while len(ret) > 0 and ret[-1] in ("<br/>", ", "):
                del ret[-1]
            return ''.join(ret)
        return '{' + ', '.join(['%s:"%s"' %
            (key, jsonHtmlRepr(obj[key], level + 1))
            for key in sorted(obj.keys())]) + '}'
    elif isinstance(obj, list):
        ret = '[' + ', '.join([jsonHtmlRepr(sub_obj, level + 1)
            for sub_obj in obj]) + ']'
        if level == 0:
            return htmlEscape(ret)
        return ret
    return '???'

#===============================================
def vcfRepr(vcf_content):
    output = StringIO()
    collect_str = ""
    for fld in vcf_content.split('\t'):
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
    return output.getvalue()

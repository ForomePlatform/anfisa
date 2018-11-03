import logging, traceback, numbers
from StringIO import StringIO
from xml.sax.saxutils import escape

#===============================================
def _not_empty(val):
    return not not val

def _htmlEscape(val):
    if val is None or val == "":
        return val
    return escape(str(val))

#===============================================
def attrHtmlRepr(attr_h, obj):
    repr_text = None
    val_obj = obj.get(attr_h.getName()) if obj else None
    try:
        if attr_h.isSeq() and val_obj:
            repr_text = ', '.join(filter(_not_empty,
                [_htmlRepr(attr_h, it_obj) for it_obj in val_obj]))
        elif val_obj or val_obj is 0:
            repr_text = _htmlRepr(attr_h, val_obj)
        if repr_text is None:
            return ("-", "none")
        if not repr_text:
            return ("&emsp;", "none")
        return (repr_text, attr_h.getMainKind())
    except Exception:
        rep = StringIO()
        traceback.print_exc(file = rep, limit = 10)
        logging.error(
            ("Problem with attribute %s: obj = %r Stack:\n" %
                (attr_h.getPath(), val_obj)) + rep.getvalue())
        return ("???", "none")

#===============================================
def _htmlRepr(attr_h, it_obj):
    if not it_obj and it_obj is not 0:
        return None
    if attr_h.hasKind("json") or attr_h.getTpCnt().detectType() == "dict":
        return _jsonRepr(it_obj)
    value = it_obj
    if not value:
        return None
    if attr_h.hasKind("link"):
        value = attr_h.normLink(value)
        return ('<span title="%s"><a href="%s" target="blank">'
            'link</a></span>' % (value, value))
    else:
        return _htmlEscape(value)

#===============================================
def _jsonRepr(obj, level = 0):
    if obj is None:
        return "null"
    if isinstance(obj, basestring) or isinstance(obj, numbers.Number):
        return str(obj)
    elif isinstance(obj, dict):
        if level < 2:
            ret = []
            for key in sorted(obj.keys()):
                if level == 0:
                    ret.append("<b>%s</b>: " % _htmlEscape(key))
                    ret.append("<br/>")
                else:
                    ret.append("%s: " % _htmlEscape(key))
                rep_val = _jsonRepr(obj[key], level + 1)
                if level == 0:
                    rep_val = _htmlEscape(rep_val)
                ret.append(rep_val)
                ret.append(", ")
                if level == 0:
                    ret.append("<br/>")
            while len(ret) > 0 and ret[-1] in ("<br/>", ", "):
                del ret[-1]
            return ''.join(ret)
        return '{' + ', '.join(['%s:"%s"' %
            (key, _jsonRepr(obj[key], level + 1))
            for key in sorted(obj.keys())]) + '}'
    elif isinstance(obj, list):
        ret = '[' + ', '.join([_jsonRepr(sub_obj, level + 1)
            for sub_obj in obj]) + ']'
        if level == 0:
            return _htmlEscape(ret)
        return ret
    return '???'

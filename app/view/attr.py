import numbers, traceback, logging
from StringIO import StringIO
from xml.sax.saxutils import escape

#===============================================
def _not_empty(val):
    return not not val

def _not_none(val):
    return val is not None

#===============================================
class AttrH:
    def __init__(self, name, kind = None, title = None,
            attrs = None, is_seq = False):
        self.mName = name
        self.mTitle = (title if title is not None else name)
        self.mKind = kind if kind else "norm"
        assert attrs is None or not is_seq
        assert attrs is None or kind != "json"
        self.mAttrs = attrs
        self.mIsSeq = is_seq
        self.mPath = None

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return self.mAttrs

    def isSeq(self):
        return self.mIsSeq

    def getKind(self):
        return self.mKind

    def _feedAttrPath(self, path, registry):
        if self.mName is None:
            self.mPath = "None"
            return
        self.mPath = a_path = path + '/' + self.mName
        if self.mAttrs is not None:
            for a_name in self.mAttrs:
                registry.add(path + '/' + a_name)
            return
        registry.add(a_path)
        if self.mIsSeq:
            registry.add(a_path + "[]")
        if self.mKind in ("json", "hidden"):
            registry.add(a_path + "*")
            return

    def getHtmlRepr(self, obj):
        repr_text = None
        val_obj = obj.get(self.mName) if obj else None
        try:
            if self.mAttrs and obj:
                repr_text = ' '.join(filter(_not_none,
                    [self._htmlEscape(obj.get(a_name))
                    for a_name in self.mAttrs]))
                if not repr_text:
                    repr_text = None
                else:
                    repr_text = repr_text.strip()
            elif self.mIsSeq and val_obj:
                repr_text = ', '.join(filter(_not_empty,
                    [self._htmlRepr(it_obj) for it_obj in val_obj]))
            elif val_obj:
                repr_text = self._htmlRepr(val_obj)
            if repr_text is None:
                return ("-", "none")
            if not repr_text:
                return ("&emsp;", "none")
            return (repr_text, self.mKind)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep, limit = 10)
            logging.error(
                ("Problem with attribute %s: obj = %r Stack:\n" %
                    (self.mPath, val_obj)) + rep.getvalue())

            return ("???", "none")

    @staticmethod
    def _htmlEscape(val):
        if val is None or val == "":
            return val
        #return escape(str(val).replace('_', ' '))
        return escape(str(val))

    @classmethod
    def _jsonRepr(cls, obj, level = 0):
        if obj is None:
            return "null"
        if isinstance(obj, basestring) or isinstance(obj, numbers.Number):
            return str(obj)
        elif isinstance(obj, dict):
            if level < 2:
                ret = []
                for key in sorted(obj.keys()):
                    if level == 0:
                        ret.append("<b>%s</b>: " % cls._htmlEscape(key))
                        ret.append("<br/>")
                    else:
                        ret.append("%s: " % cls._htmlEscape(key))
                    rep_val = cls._jsonRepr(obj[key], level + 1)
                    if level == 0:
                        rep_val = cls._htmlEscape(rep_val)
                    ret.append(rep_val)
                    ret.append(", ")
                    if level == 0:
                        ret.append("<br/>")
                while len(ret) > 0 and ret[-1] in ("<br/>", ", "):
                    del ret[-1]
                return ''.join(ret)
            return '{' + ', '.join(['%s:"%s"' %
                (key, cls._jsonRepr(obj[key], level + 1))
                for key in sorted(obj.keys())]) + '}'
        elif isinstance(obj, list):
            ret = '[' + ', '.join([cls._jsonRepr(sub_obj, level + 1)
                for sub_obj in obj]) + ']'
            if level == 0:
                return cls._htmlEscape(ret)
            return ret
        return '???'

    def _htmlRepr(self, it_obj):
        if not it_obj:
            return None
        if self.mKind == "json":
            return self._jsonRepr(it_obj)
        value = it_obj
        if not value:
            return None
        if self.mKind == "link":
            return ('<span title="%s"><a href="%s" target="blank">'
                'link</a></span>' % (value, value))
        else:
            return self._htmlEscape(value)


import numbers, traceback, logging
from StringIO import StringIO
from xml.sax.saxutils import escape

from app.model.types import Types
#===============================================
def _not_empty(val):
    return not not val

def _not_none(val):
    return val is not None

#===============================================
class AttrH:
    sBaseHostFrom = None
    sBaseHostTo   = None

    @classmethod
    def setupBaseHostReplacement(cls, host_from, host_to):
        cls.sBaseHostFrom = host_from
        cls.sBaseHostTo   = host_to

    @classmethod
    def getJSonOptions(cls):
        return {"link_host": [cls.sBaseHostFrom, cls.sBaseHostTo]}

    @classmethod
    def normLink(cls, str):
        if cls.sBaseHostFrom and str:
            return str.replace(cls.sBaseHostFrom, cls.sBaseHostTo)
        return str

    def __init__(self, name, kind = None, title = None,
            is_seq = False, tp_cnt = None):
        self.mName = name
        self.mTitle = (title if title is not None else name)
        self.mKinds = kind.split() if kind else ["norm"]
        self.mIsSeq = is_seq
        self.mResearchOnly = "research" in self.mKinds
        self.mPath = None
        self.mTpCnt = tp_cnt

    def copy(self):
        assert self.mTpCnt is None
        return AttrH(self.mName, " ".join(self.mKinds), self.mTitle,
            self.mIsSeq)

    def _setTpCnt(self, tp_cnt):
        self.mTpCnt = tp_cnt

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def isSeq(self):
        return self.mIsSeq

    def hasKind(self, kind):
        return kind in self.mKinds

    def getType(self):
        return Types.filterTypeKind(self.mKinds)

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getTpCnt(self):
        return self.mTpCnt

    def getJSonObj(self):
        return {
            "name": self.mName, "kind": " ".join(self.mKinds),
            "title": self.mTitle, "is_seq": self.mIsSeq,
            "cnt": self.mTpCnt.repJSon() if self.mName is not None else None,
            "path": self.mPath}

    def _feedAttrPath(self, path, registry):
        if self.mName is None:
            self.mPath = "None"
            return
        a_path = path + '/' + self.mName
        self.mPath = a_path
        registry.add(a_path)
        if self.mIsSeq:
            registry.add(a_path + "[]")
        if "json" in self.mKinds or "hidden" in self.mKinds:
            registry.add(a_path + "*")
            return

    def getHtmlRepr(self, obj):
        repr_text = None
        val_obj = obj.get(self.mName) if obj else None
        try:
            if self.mIsSeq and val_obj:
                repr_text = ', '.join(filter(_not_empty,
                    [self._htmlRepr(it_obj) for it_obj in val_obj]))
            elif val_obj or val_obj is 0:
                repr_text = self._htmlRepr(val_obj)
            if repr_text is None:
                return ("-", "none")
            if not repr_text:
                return ("&emsp;", "none")
            return (repr_text, self.mKinds[0])
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
        if not it_obj and it_obj is not 0:
            return None
        if "json" in self.mKinds or self.mTpCnt.detectType() == "dict":
            return self._jsonRepr(it_obj)
        value = it_obj
        if not value:
            return None
        if "link" in self.mKinds:
            value = self.normLink(value)
            return ('<span title="%s"><a href="%s" target="blank">'
                'link</a></span>' % (value, value))
        else:
            return self._htmlEscape(value)

import logging, traceback
from io import StringIO

from .view_repr import jsonHtmlRepr, htmlEscape
#===============================================
class AttrH:
    sBaseHostFrom = None
    sBaseHostTo   = None

    @classmethod
    def setupLinkBase(cls, host_from, host_to):
        cls.sBaseHostFrom = host_from
        cls.sBaseHostTo   = host_to

    @classmethod
    def getJSonOptions(cls):
        return {"link_host": [cls.sBaseHostFrom, cls.sBaseHostTo]}

    @classmethod
    def normLink(cls, value):
        if cls.sBaseHostFrom and value:
            return value.replace(cls.sBaseHostFrom, cls.sBaseHostTo)
        return value

    #===============================================
    def __init__(self, name, kind = None, title = None,
            is_seq = False, tooltip = None):
        self.mAspect = None
        self.mName = name
        self.mTitle = (title if title is not None else name)
        self.mKinds = kind.split() if kind else ["norm"]
        self.mToolTip = tooltip
        self.mIsSeq = is_seq
        self.mResearchOnly = "research" in self.mKinds

    def setAspect(self, asp):
        self.mAspect = asp

    def reset(self, kind, is_seq):
        self.mKinds = kind.split() if kind else ["norm"]
        self.mIsSeq = is_seq

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def isSeq(self):
        return self.mIsSeq

    def getToolTip(self):
        return self.mToolTip

    def hasKind(self, kind):
        return kind in self.mKinds

    def getMainKind(self):
        return self.mKinds[0]

    def getKinds(self):
        return iter(self.mKinds)

    def getFullName(self):
        return self.mAspect.getName() + '.' + self.mName

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    #===============================================
    def dump(self):
        ret = {
            "name": self.mName, "kind": " ".join(self.mKinds),
            "title": self.mTitle, "is_seq": self.mIsSeq}
        if self.mToolTip:
            ret["tooltip"] = self.mToolTip
        return ret

    @classmethod
    def load(cls, data):
        return cls(data["name"], data["kind"], data["title"],
            is_seq = data["is_seq"], tooltip = data.get("tooltip"))

    #===============================================
    def htmlRepr(self, obj, top_rec_obj):
        try:
            val_obj = obj.get(self.mName) if obj else None
            repr_text = None
            if val_obj is 0:
                return ("0", self.getMainKind())
            if val_obj:
                if self.mIsSeq:
                    seq = []
                    for it_obj in val_obj:
                        it_repr = self._htmlRepr(it_obj)
                        if it_repr:
                            seq.append(it_repr)
                    repr_text = ', '.join(seq)
                else:
                    repr_text = self._htmlRepr(val_obj)
            if repr_text is None:
                return ("-", "none")
            if not repr_text:
                return ("&emsp;", "none")
            return (repr_text, self.getMainKind())
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep, limit = 10)
            logging.error(
                ("Problem with attribute %s: obj = %r Stack:\n" %
                    (self.getFullName(), val_obj)) + rep.getvalue())
            return ("???", "none")

    def _htmlRepr(self, value):
        if not value and value is not 0:
            return None
        if "json" in self.mKinds:
            return jsonHtmlRepr(value)
        if not value:
            return None
        if "link" in self.mKinds:
            link = self.normLink(value)
            return ('<span title="%s"><a href="%s" target="blank">'
                'link</a></span>' % (link, link))
        return htmlEscape(value)


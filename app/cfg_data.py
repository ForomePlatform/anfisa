import numbers, traceback, logging
from StringIO import StringIO
from xml.sax.saxutils import escape
#===============================================
class AspectH:
    def __init__(self, name, title, json_container = False, attrs = None,
            ignored = False, kind = None, col_groups = None):
        self.mName     = name
        self.mTitle    = title
        self.mJsonContainer = (self.mName
            if json_container is False else json_container)
        self.mAttrs = (attrs if attrs else [])
        self.mIgnored  = ignored
        self.mKind = kind if kind else "norm"
        self.mColGroups = col_groups

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getJsonContainer(self):
        return self.mJsonContainer

    def getAttrs(self):
        return self.mAttrs

    def getColGroups(self):
        return self.mColGroups

    def isIgnored(self):
        return self.mIgnored

    def getAspectKind(self):
        return self.mKind

    def _feedAttrPath(self, registry):
        path = self.mJsonContainer
        if path is None:
            path = "/"
        else:
            path = "/" + path
            registry.add(path)
            path += '/'
        if self.mColGroups is not None:
            for grp in self.mColGroups:
                grp_path = path + grp.getAttr()
                registry.add(grp_path)
                grp_path += "[]"
                registry.add(grp_path)
                for attr in self.mAttrs:
                    attr._feedAttrPath(grp_path + "/", registry)
        else:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)

#===============================================
def _not_empty(val):
    return not not val

def _not_none(val):
    return val is not None

class AttrH:
    def __init__(self, name, kind = None, title = None,
            attrs = None, is_seq = False):
        self.mName = name
        self.mTitle = (title
            if title is not None else str(name).replace('_', ' '))
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

    def _feedAttrPath(self, path, registry):
        if self.mName is None:
            self.mPath = "None"
            return
        self.mPath = a_path = path + self.mName
        if self.mAttrs:
            for a_name in self.mAttrs:
                registry.add(path + a_name)
            return
        registry.add(a_path)
        if self.mKind == "json":
            registry.add(a_path + "*")
            return
        if self.mIsSeq:
            a_path += "[]"
            registry.add(a_path)

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
        return escape(str(val).replace('_', ' '))

    @classmethod
    def _jsonRepr(cls, obj):
        if obj is None:
            return "null"
        if isinstance(obj, basestring) or isinstance(obj, numbers.Number):
            return str(obj)
        elif isinstance(obj, dict):
            return '{' + ', '.join(['%s:"%s"' %
                (key, cls._jsonRepr(obj[key]))
                for key in sorted(obj.keys())]) + '}'
        elif isinstance(obj, list):
            return '[' + ', '.join([cls._jsonRepr(sub_obj)
                for sub_obj in obj]) + ']'
        return '???'

    def _htmlRepr(self, it_obj):
        if not it_obj:
            return None
        if self.mKind == "json":
            value = self._jsonRepr(it_obj)
        else:
            value = it_obj
        if not value:
            return None
        if self.mKind == "link":
            return ('<span title="%s"><a href="%s" target="blank">link</a></span>' %
                (value, value))
        else:
            return self._htmlEscape(value)

#===============================================
class ColGroupH:
    def __init__(self, attr, title):
        self.mAttr  = attr
        self.mTitle = title

    def getAttr(self):
        return self.mAttr

    def getTitle(self):
        return self.mTitle

#===============================================
class ObjectAttributeChecker:
    def __init__(self, aspects, ignore_attrs):
        self.mGoodAttrs = set()
        self.mBadAttrs = set()
        for attr in ignore_attrs:
            self.mGoodAttrs.add(attr)
        for asp in aspects:
            asp._feedAttrPath(self.mGoodAttrs)

    def _feedAttrs(self, attrs, path):
        for attr in attrs:
            attr._feedAttrPath(path, self.mGoodAttrs)

    def checkObj(self, obj, path = ""):
        if path and path not in self.mGoodAttrs:
            self.mBadAttrs.add(path)
            return
        if obj is None:
            return
        if isinstance(obj, basestring) or isinstance(obj, numbers.Number):
            return
        elif isinstance(obj, dict):
            for a_name, sub_obj in obj.items():
                self.checkObj(sub_obj, path + '/' + a_name)
        elif isinstance(obj, list):
            for sub_obj in obj:
                self.checkObj(sub_obj, path + "[]")
        else:
            logging.error("BAD:path=%s: %r" % (path, obj))
            self.mBadAttrs.add(path + "?")

    def finishUp(self):
        if len(self.mBadAttrs) > 0:
            good_path_heads = set()
            ign_path_set = set()
            for path in self.mGoodAttrs:
                if path.endswith('*'):
                    good_path_heads.add(path[:-1])
            for bad_path in self.mBadAttrs:
                for path in good_path_heads:
                    if (bad_path.startswith(path) and
                            bad_path[len(path):][:1] in '/['):
                        ign_path_set.add(bad_path)
                        break
            self.mBadAttrs -= ign_path_set
        return len(self.mBadAttrs) == 0

        return len(self.mBadAttrs) == 0

    def reportBadAttributes(self, output):
        print >> output, "Bad attribute path list(%d):" % len(self.mBadAttrs)
        for path in sorted(self.mBadAttrs):
            print >> output, "\t%s" % path

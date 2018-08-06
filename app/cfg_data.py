import numbers, traceback, logging
from StringIO import StringIO
from xml.sax.saxutils import escape
#===============================================
#                if class_name == "link":
#                    vv = '<a href="%s" target="blank">link</a>' % vv

#            if val:
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

class AttrH:
    def __init__(self, name, title = None, kind = None,
            attrs = None, is_seq = False, dict_keys = None):
        self.mName = name
        self.mTitle = (title
            if title is not None else str(name).replace('_', ' '))
        self.mKind = kind if kind else "norm"
        assert attrs is None or not is_seq
        assert attrs is None or dict_keys is None
        self.mAttrs = attrs
        self.mIsSeq = is_seq
        self.mDictKeys = dict_keys

    def getName(self):
        return self.mName

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return self.mAttrs

    def isSeq(self):
        return self.mIsSeq

    def getDictKeys(self):
        return self.mDictKeys

    def _feedAttrPath(self, path, registry):
        if self.mName is None:
            return
        if self.mAttrs:
            for a_name in self.mAttrs:
                registry.add(path + a_name)
            return
        a_path = path + self.mName
        registry.add(a_path)
        if self.mIsSeq:
            a_path += "[]"
            registry.add(a_path)
        if self.mDictKeys:
            for key in self.mDictKeys:
                registry.add(a_path + "/" + key)

    def getHtmlRepr(self, obj):
        try:
            repr_text = None
            val_obj = obj.get(self.mName) if obj else None
            if self.mAttrs and obj:
                repr_text = ' '.join(filter(_not_empty,
                    [self._htmlEscape(obj.get(a_name))
                    for a_name in self.mAttrs]))
            elif self.mIsSeq and val_obj:
                repr_text = ', '.join(filter(_not_empty,
                    [self._htmlRepr(it_obj) for it_obj in val_obj]))
            elif val_obj:
                repr_text = self._htmlRepr(val_obj)
            if not repr_text:
                return ("-", "none")
            return (repr_text, self.mKind)
        except Exception:
            rep = StringIO()
            traceback.print_exc(file = rep, limit = 10)
            logging.error("Stack:\n" + rep.getvalue())

            return ("???", "none")

    @staticmethod
    def _htmlEscape(val):
        if not val:
            return ""
        return escape(str(val).replace('_', ' '))


    def _htmlRepr(self, it_obj):
        if not it_obj:
            return None
        if self.mDictKeys:
            value = ' '.join(filter(_not_empty,
                [it_obj.get(key) for key in self.mDictKeys]))
        else:
            value = it_obj
        if not value:
            return None
        if self.mKind == "link":
            return '<a href="%s" target="blank">link</a>' % value
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
            print ("BAD:path=%s: %r" % (path, obj))
            self.mBadAttrs.add(path + "?")

    def isOK(self):
        return len(self.mBadAttrs) == 0

    def reportBadAttributes(self, output):
        print >> output, "Bad attribute path list(%d):" % len(self.mBadAttrs)
        for path in sorted(self.mBadAttrs):
            print >> output, "\t%s" % path

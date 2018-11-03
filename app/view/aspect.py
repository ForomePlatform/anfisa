from xml.sax.saxutils import escape
from StringIO import StringIO

from .attr_repr import attrHtmlRepr
#===============================================
class AspectH:
    def __init__(self, name, title, source, field = None,
            attrs = None, ignored = False, col_groups = None,
            research_only = False):
        self.mName     = name
        self.mTitle    = title
        self.mSource   = source
        self.mField    = field
        self.mAttrs    = attrs
        self.mIgnored  = ignored
        self.mResearchOnly = research_only
        self.mColGroups = col_groups
        assert self.mSource in ("view", "data")
        if self.mColGroups is not None:
            assert self.mField is None
        if self.mIgnored and self.mAttrs is None:
            self.mAttrs = []
        self.mTpCnt = None

    def copy(self):
        assert self.mTpCnt is None
        return AspectH(self.mName, self.mTitle, self.mSource, self.mField,
            [attr_h.copy() for attr_h in self.mAttrs], self.mIgnored,
            self.mColGroups, self.mResearchOnly)

    def _setTpCnt(self, tp_cnt):
        self.mTpCnt = tp_cnt

    def _addAttr(self, attr_h):
        self.mAttrs.append(attr_h)

    def getName(self):
        return self.mName

    def getSource(self):
        return self.mSource

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return self.mAttrs

    def getField(self):
        return self.mField

    def getColGroups(self):
        return self.mColGroups

    def getTpCnt(self):
        return self.mTpCnt

    def isIgnored(self):
        return self.mIgnored

    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getAspectKind(self):
        return {"view": "norm", "data": "tech"}[self.mSource]

    def setRecommendedAttrs(self, attrs):
        self.mAttrs = attrs

    def _feedAttrPath(self, registry):
        path_seq = ['/' + self.mSource]
        registry.add(path_seq[0])
        if self.mField:
            path_seq[0] += '/' + self.mField
            registry.add(path_seq[0])
        if self.mColGroups is not None:
            grp_path_seq = []
            for idx in range(self.mColGroups.getCount()):
                grp_attr = self.mColGroups.getAttr(idx)
                grp_path_seq.append(path_seq[0][:])
                grp_path_seq[-1] += '/' + grp_attr
                registry.add(grp_path_seq[-1])
                grp_path_seq[-1] += '[]'
                registry.add(grp_path_seq[-1])
            path_seq = grp_path_seq
        for path in path_seq:
            for attr in self.mAttrs:
                attr._feedAttrPath(path, registry)

    def getJSonObj(self):
        ret = {
            "name": self.mName, "title": self.mTitle,
            "source": self.mSource,
            "field": self.mField, "ignored": self.mIgnored,
            "research": self.mResearchOnly,
            "attrs": [attr_h.getJSonObj() for attr_h in self.mAttrs]}
        if self.mColGroups is not None:
            ret["col_groups"] = self.mColGroups.getJSonObj()
        return ret

    #===============================================
    def getJSonRepr(self, rec_data, research_mode):
        ret = {
            "name": self.mName,
            "title": self.mTitle,
            "kind": self.getAspectKind(),
            "title": self.mTitle}
        if self.mName == "input":
            return self._getJSonInputRepr(rec_data, ret)
        objects = [rec_data[self.getSource()]]
        if self.getField():
            objects = [objects[0][self.getField()]]
        prefix_head = None
        if self.getColGroups():
            objects, prefix_head = self.getColGroups().prepareObjects(objects)
        fld_data = dict()
        for attr in self.getAttrs():
            if (attr.getName() is None or
                    attr.checkResearchBlock(research_mode) or
                    attr.hasKind("hidden")):
                continue
            values = [attrHtmlRepr(attr, obj) for obj in objects]
            if not all([vv == ('-', "none") for vv in values]):
                fld_data[attr.getName()] = values
        ret["type"] = "table"
        ret["columns"] = len(objects)
        if prefix_head:
            ret["colhead"] = [[escape(title), count]
                for title, count in prefix_head]
        rows = []
        for attr in self.getAttrs():
            if attr.getName() is None:
                rows.append([])
                continue
            if attr.getName() not in fld_data:
                continue
            rows.append([attr.getName(), escape(attr.getTitle()),
                [[val, class_name]
                    for val, class_name in fld_data[attr.getName()]]])
        ret["rows"] = rows
        return ret

    def _getJSonInputRepr(self, rec_data, ret):
        ret["type"] = "pre"
        if "input" not in rec_data["data"]:
            return ret
        output = StringIO()
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
        ret["content"] = output.getvalue()
        return ret

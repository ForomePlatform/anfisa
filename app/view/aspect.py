import logging
from xml.sax.saxutils import escape

from .attr import AttrH
from .view_repr import vcfRepr
from .colgrp import ColGroupsH

#===============================================
class AspectH:
    def __init__(self, name, title, source, field = None,
            attrs = None, ignored = False, col_groups = None,
            research_only = False, mode = "dict"):
        self.mName     = name
        self.mTitle    = title
        self.mSource   = source
        self.mField    = field
        self.mAttrs    = None
        self.mIgnored  = ignored
        self.mResearchOnly = research_only
        self.mColGroups = col_groups
        self.mMode      = mode
        assert self.mSource in ("view", "data")
        if self.mColGroups is not None:
            assert self.mField is None

        if self.mIgnored or self.mMode != "dict":
            self.mAttrs = []
        if attrs is not None:
            self.setAttributes(attrs)

    def __getitem__(self, idx):
        return self.mAttrs[idx]

    def find(self, name):
        for idx, attr_h in enumerate(self.mAttrs):
            if attr_h.getName() == name:
                return idx
        return -1

    def setAttributes(self, attrs):
        self.mAttrs = attrs
        for attr_h in self.mAttrs:
            attr_h.setAspect(self)

    def addAttr(self, attr_h, idx = -1):
        attr_h.setAspect(self)
        if idx < 0:
            self.mAttrs.append(attr_h)
        else:
            self.mAttrs.insert(idx, attr_h)

    def delAttr(self, attr_h):
        self.mAttrs.remove(attr_h)

    def getName(self):
        return self.mName

    def getSource(self):
        return self.mSource

    def getTitle(self):
        return self.mTitle

    def getAttrs(self):
        return iter(self.mAttrs)

    def getField(self):
        return self.mField

    def getColGroups(self):
        return self.mColGroups

    def isIgnored(self):
        return self.mIgnored

    def getMode(self):
        return self.mMode

    #===============================================
    def dump(self):
        ret = {
            "name": self.mName,
            "title": self.mTitle,
            "source": self.mSource,
            "ignored": self.mIgnored,
            "research": self.mResearchOnly,
            "mode": self.mMode,
            "attrs": [attr_h.dump() for attr_h in self.mAttrs]}
        if self.mField is not None:
            ret["field"] = self.mField
        if self.mColGroups is not None:
            ret["col_groups"] = self.mColGroups.dump()
        return ret

    @classmethod
    def load(cls, data):
        return cls(data["name"], data["title"], data["source"],
            field = data.get("field"),
            attrs = [AttrH.load(it) for it in data["attrs"]],
            ignored = data["ignored"],
            col_groups = ColGroupsH.load(data.get("col_groups")),
            research_only = data["research"],
            mode = data["mode"])

    #===============================================
    def checkResearchBlock(self, research_mode):
        return (not research_mode) and self.mResearchOnly

    def getViewRepr(self, rec_data, research_mode, details = None):
        ret = {
            "name": self.mName,
            "title": self.mTitle,
            "kind": {"view": "norm", "data": "tech"}[self.mSource]}
        if self.mName == "input":
            ret["type"] = "pre"
            if "input" in rec_data["data"]:
                ret["content"] = vcfRepr(rec_data["data"]["input"])
            return ret
        ret["type"] = "table"
        objects = [rec_data[self.mSource]]
        if self.mField:
            objects = [objects[0][self.mField]]
        hit_columns = None
        if self.mColGroups:
            objects, prefix_head, hit_columns = self.mColGroups.formColumns(
                objects, details)
            if prefix_head:
                ret["colhead"] = [[escape(title), count]
                    for title, count in prefix_head]
        ret["columns"] = len(objects)
        fld_data = dict()
        for attr in self.mAttrs:
            if (attr.getName() is None or
                    attr.checkResearchBlock(research_mode) or
                    attr.hasKind("hidden")):
                continue
            values = []
            for obj in objects:
                obj_repr = attr.htmlRepr(obj, rec_data)
                if obj_repr is not None and obj_repr != ('-', "none"):
                    values.append(obj_repr)
            if len(values) > 0:
                fld_data[attr.getName()] = values
        rows = []
        for attr in self.getAttrs():
            a_name = attr.getName()
            if a_name is None:
                rows.append([])
                continue
            a_values = fld_data.get(a_name)
            if not a_values:
                continue
            rows.append([a_name, escape(attr.getTitle()),
                [[val, class_name] for val, class_name in a_values]])
            if attr.getToolTip():
                rows[-1].append(attr.getToolTip())
        if hit_columns:
            for row in rows:
                for idx, td_info in enumerate(row[2]):
                    if idx in hit_columns:
                        td_info[1] += ' hit'
        ret["rows"] = rows
        return ret

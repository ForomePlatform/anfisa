#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from xml.sax.saxutils import escape

from .attr import AttrH
from .view_repr import vcfRepr
from .colgrp import ColGroupsH

#===============================================
class AspectH:
    def __init__(self, name, title, source, field = None,
            attrs = None, ignored = False, col_groups = None,
            mode = "dict"):
        self.mName     = name
        self.mTitle    = title
        self.mSource   = source
        self.mField    = field
        self.mAttrs    = None
        self.mIgnored  = ignored
        self.mColGroups = col_groups
        self.mMode      = mode
        self.mColumnMarkupF = None
        assert self.mSource in ("_view", "__data"), (
            "name=" + name + " source=" + self.mSource)

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

    def setColumnMarkup(self, markup_func):
        self.mColumnMarkupF = markup_func

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
            mode = data["mode"])

    #===============================================
    def getViewRepr(self, rec_data, view_context = None):
        ret_handle = {
            "name": self.mName,
            "title": self.mTitle,
            "kind": {"_view": "norm", "__data": "tech"}[self.mSource]}
        if self.mName == "input":
            ret_handle["type"] = "pre"
            if "input" in rec_data["__data"]:
                ret_handle["content"] = vcfRepr(rec_data["__data"]["input"])
            return ret_handle
        ret_handle["type"] = "table"
        ret_handle["parcontrol"] = None
        ret_handle["colgroup"] = None
        objects = [rec_data[self.mSource]]
        if self.mField:
            objects = [objects[0][self.mField]]
        if self.mColGroups:
            objects = self.mColGroups.formColumns(ret_handle, objects)
        ret_handle["columns"] = len(objects)
        fld_data = dict()
        for attr in self.mAttrs:
            if (attr.getName() is None
                    or attr.hasKind("hidden")):
                continue
            values = []
            cnt_good = 0
            for obj in objects:
                obj_repr = attr.htmlRepr(obj, view_context)
                if obj_repr is not None:
                    cnt_good += (obj_repr != ('-', "none"))
                    values.append(obj_repr)
            if cnt_good > 0:
                fld_data[attr.getName()] = values
        rows = []
        for attr in self.getAttrs():
            a_name = attr.getName()
            if a_name is None:
                rows.append(None)
                continue
            a_values = fld_data.get(a_name)
            if not a_values:
                continue
            row = {"name": a_name,
                "title": attr.getTitle(),
                "cells": [[val, class_name] for val, class_name in a_values]}
            if attr.getToolTip():
                row["tooltip"] = attr.getToolTip().replace("'", '"')
            if attr.getRenderMode():
                row["render"] = attr.getRenderMode()
            rows.append(row)
        ret_handle["rows"] = rows
        if self.mColumnMarkupF is not None:
            self.mColumnMarkupF(ret_handle, view_context, self)
        return ret_handle

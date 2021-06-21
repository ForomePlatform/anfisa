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

from collections import defaultdict
from copy import deepcopy

from .zone import ZoneH
#===============================================
class TagsManager(ZoneH):
    def __init__(self, ds_h, check_tag_list):
        ZoneH.__init__(self, ds_h, "_tags")
        self.mTagSets = defaultdict(set)
        self.mMarkedSet = set()
        self.mCheckTags = check_tag_list

    def getName(self):
        return "_tags"

    def refreshTags(self):
        self.mTagSets = defaultdict(set)
        self.mMarkedSet = set()
        for tags_info in self.getDS().getSolEnv().iterEntries("tags"):
            rec_key, tags_data = tags_info[:2]
            if not tags_data:
                continue
            rec_no = self.getDS().getRecNoByKey(rec_key)
            if rec_no is not None:
                for tag in tags_data.keys():
                    self.mTagSets[tag].add(rec_no)
                    self.mMarkedSet.add(rec_no)

    def getOpTagList(self):
        return sorted(set(self.mTagSets.keys()) - set(self.mCheckTags))

    def getTagList(self):
        return self.getOpTagList() + self.mCheckTags

    def getVariants(self):
        return self.getTagList()

    def updateRec(self, rec_no, tags_data):
        to_del = []
        for key, val in tags_data.items():
            if not key or val is False:
                to_del.append(key)
        for key in to_del:
            del tags_data[key]

        rec_key = self.getDS().getRecKey(rec_no)
        prev_data = self.getDS().getSolEnv().getEntry("tags", rec_key)[0]
        if (prev_data is None
                or any(val != tags_data.get(key)
                    for key, val in prev_data.items())
                or any(val != prev_data.get(key)
                    for key, val in tags_data.items())):
            self.getDS().getSolEnv().modifyEntry(self.getDS().getName(),
                "tags", "UPDATE", rec_key, tags_data)

    def getTagListInfo(self):
        return {
            "check-tags": self.mCheckTags[:],
            "op-tags": self.getOpTagList()}

    def getRecTags(self, rec_no):
        rec_key = self.getDS().getRecKey(rec_no)
        return self.getDS().getSolEnv().getEntry("tags", rec_key)[0]

    def makeRecReport(self, rec_no):
        ret = self.getTagListInfo()
        rec_key = self.getDS().getRecKey(rec_no)
        tags_data, upd_time, upd_from = self.getDS().getSolEnv().getEntry(
            "tags", rec_key)
        ret["rec-tags"] = tags_data if tags_data is not None else dict()
        ret["upd-time"] = upd_time
        ret["upd-from"] = upd_from
        return ret

    def getRestrictF(self, variants, restrict_f = None):
        if restrict_f is not None:
            return lambda rec_no: (
                restrict_f(rec_no) and self.checkVariants(rec_no, variants))
        return lambda rec_no: self.checkVariants(rec_no, variants)

    def checkVariants(self, rec_no, variants):
        for tag_name in variants:
            tag_set = self.mTagSets.get(tag_name)
            if tag_set and rec_no in tag_set:
                return True
        return False

    def reportSelectTag(self, tag_name):
        tag_list = self.getTagList()
        if tag_name and tag_name not in tag_list:
            tag_name = None
        rep = {
            "tag-list": tag_list,
            "tag": tag_name,
            "tags-state": self.getDS().getSolEnv().getIntVersion("tags"),
            "tags-rec-list": sorted(self.mMarkedSet)}
        if tag_name:
            rep["tag-rec-list"] = sorted(self.mTagSets[tag_name])
        return rep

    def selectionTagging(self, tag_name, rec_no_seq):
        assert tag_name and tag_name not in self.mCheckTags, (
            "Missing tag: " + tag_name)
        new_tag_keys = {self.getDS().getRecKey(rec_no)
            for rec_no in rec_no_seq}
        to_update_seq = []
        for tags_info in self.getDS().getSolEnv().iterEntries("tags"):
            rec_key, tags_data = tags_info[:2]
            if tags_data is None:
                continue
            if rec_key in new_tag_keys:
                new_tag_keys.remove(rec_key)
                tags_data = deepcopy(tags_data)
                tags_data[tag_name] = "True"
                to_update_seq.append((rec_key, tags_data))
            elif tag_name in tags_data:
                tags_data = deepcopy(tags_data)
                del tags_data[tag_name]
                to_update_seq.append((rec_key, tags_data))
        simple_tag_data = {tag_name: "True"}
        for rec_key in new_tag_keys:
            to_update_seq.append((rec_key, simple_tag_data))
        for rec_key, tags_data in to_update_seq:
            self.getDS().getSolEnv().modifyEntry(self.getDS().getName(),
                "tags", "UPDATE", rec_key, tags_data)

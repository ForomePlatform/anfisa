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

from app.config.a_config import AnfisaConfig
from .zone import ZoneH
from forome_tools.job_pool import ExecutionTask
#===============================================
class TagsManager(ZoneH):
    def __init__(self, ds_h, panel_name):
        ZoneH.__init__(self, ds_h, "_tags")
        self.mTagSets = defaultdict(set)
        self.mMarkedSet = set()
        self.mCheckTags = ds_h.getStdItemData("panel._tags", panel_name)
        assert self.mCheckTags, f"Tag panel {panel_name} not found"
        self.refreshTags()

    def getName(self):
        return "_tags"

    def refreshTags(self):
        self.mTagSets = defaultdict(set)
        self.mMarkedSet = set()
        for tags_info in self.getDS().getSolEnv().iterEntries("tags"):
            rec_key, tags_data = tags_info["name"], tags_info["data"]
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

    def getVariantList(self):
        return self.getTagList()

    def updateRec(self, rec_no, tags_data):
        to_del = []
        for key, val in tags_data.items():
            if not key or val is False:
                to_del.append(key)
        for key in to_del:
            del tags_data[key]

        rec_key = self.getDS().getRecKey(rec_no)
        prev_info = self.getDS().getSolEnv().getEntry("tags", rec_key)
        prev_data = prev_info["data"] if prev_info is not None else None
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
        tags_info = self.getDS().getSolEnv().getEntry("tags", rec_key)
        if tags_info is None:
            return None
        return tags_info["data"]

    def makeRecReport(self, rec_no):
        ret = self.getTagListInfo()
        rec_key = self.getDS().getRecKey(rec_no)
        tags_info = self.getDS().getSolEnv().getEntry("tags", rec_key)
        if tags_info is not None:
            ret["rec-tags"] = tags_info["data"]
            ret["upd-time"] = tags_info.get("time")
            ret["upd-from"] = tags_info.get("from")
        else:
            ret["rec-tags"] = dict()
            ret["upd-time"] = None
            ret["upd-from"] = None
        return ret

    def getRestrictF(self, variants):
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

    def tagIsProper(self, tag_name):
        return tag_name and tag_name not in self.mCheckTags

    def macroTaggingOp(self, tag_name, rec_keys, task_h = None):
        rec_keys = deepcopy(rec_keys)
        to_update_seq = []
        if task_h is not None:
            task_h.setStatus("Preparation")
        for tags_info in self.getDS().getSolEnv().iterEntries("tags"):
            rec_key, tags_data = tags_info["name"], tags_info["data"]
            if tags_data is None:
                continue
            if rec_key in rec_keys:
                rec_keys.remove(rec_key)
                tags_data = deepcopy(tags_data)
                tags_data[tag_name] = "True"
                to_update_seq.append((rec_key, tags_data))
            elif tag_name in tags_data:
                tags_data = deepcopy(tags_data)
                del tags_data[tag_name]
                to_update_seq.append((rec_key, tags_data))
        simple_tag_data = {tag_name: "True"}

        cur_progess = 0
        if task_h is not None:
            total = len(rec_keys)
            step_cnt = total // 100
            next_cnt = step_cnt
        else:
            next_cnt = 0

        for idx, rec_key in enumerate(rec_keys):
            while next_cnt > 0 and idx > next_cnt:
                next_cnt += step_cnt
                cur_progess += 1
                task_h.setStatus("Markup records %d%s" % (cur_progess, '%'))
                AnfisaConfig.assertGoodTagName(rec_key)
            to_update_seq.append((rec_key, simple_tag_data))

        cur_progess = 0
        if task_h is not None:
            total = len(to_update_seq)
            step_cnt = total // 100
            next_cnt = step_cnt
        else:
            next_cnt = 0

        for rec_key, tags_data in to_update_seq:
            while next_cnt > 0 and idx > next_cnt:
                next_cnt += step_cnt
                cur_progess += 1
                task_h.setStatus("Update records %d%s" % (cur_progess, '%'))
            self.getDS().getSolEnv().modifyEntry(self.getDS().getName(),
                "tags", "UPDATE", rec_key, tags_data)
        if task_h is not None:
            task_h.setStatus("Done")

#===============================================
class MacroTaggingOperation(ExecutionTask):
    def __init__(self, tags_man, tag_name, rec_keys):
        ExecutionTask.__init__(self, "Macro Tagging Operation")
        self.mTagsMan = tags_man
        self.mTagName = tag_name
        self.mRecKeys = rec_keys

    def getTaskType(self):
        return "macro-tagging"

    def execIt(self):
        self.mTagsMan.macroTaggingOp(self.mTagName, self.mRecKeys)
        return {"tags-state":
                self.mTagsMan.getDS().getSolEnv().getIntVersion("tags")}

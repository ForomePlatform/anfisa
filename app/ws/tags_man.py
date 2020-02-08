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
from datetime import datetime

from app.config.a_config import AnfisaConfig
from .zone import ZoneH

#===============================================
class TagsManager(ZoneH):
    def __init__(self, ds_h, check_tag_list):
        ZoneH.__init__(self, ds_h, "_tags")
        self.mTagSets = defaultdict(set)
        self.mIntVersion = 0
        self.mMarkedSet = set()
        self.mCheckTags = check_tag_list
        self._loadDataSet()

    def getName(self):
        return "_tags"

    def getIntVersion(self):
        return self.mIntVersion

    def getMarkedSet(self):
        return self.mMarkedSet

    def _loadDataSet(self):
        sol_env = self.getDS().getSolEnv()
        for rec_no, rec_key in self.getDS().iterRecKeys():
            data_obj = sol_env.getTagsData(rec_key)
            if data_obj is not None:
                for tag in data_obj.keys():
                    if self._goodKey(tag):
                        self.mTagSets[tag].add(rec_no)
                        self.mMarkedSet.add(rec_no)
        self.mIntVersion += 1

    def getOpTagList(self):
        return sorted(set(self.mTagSets.keys()) - set(self.mCheckTags))

    def getTagList(self):
        return self.getOpTagList() + self.mCheckTags

    def getVariants(self):
        return self.getTagList()

    @staticmethod
    def _goodPair(key_value):
        key, value = key_value
        return (key and (key[0] != '_' or key == "_note")
            and value not in (None, False))

    @staticmethod
    def _goodKey(key):
        return key and (key[0] != '_' or key == "_note")

    def updateRec(self, rec_no, tags_to_update):
        rec_key = self.getDS().getRecKey(rec_no)
        return self._changeRecord(rec_no, rec_key,
            self.getDS().getSolEnv().getTagsData(rec_key), tags_to_update)

    def getTagListInfo(self):
        return {
            "check-tags": self.mCheckTags[:],
            "op-tags": self.getOpTagList()}

    def getRecTags(self, rec_no):
        return self._getRecData(rec_no)[0]

    def _getRecData(self, rec_no):
        rec_key = self.getDS().getRecKey(rec_no)
        rec_data = self.getDS().getSolEnv().getTagsData(rec_key)
        if rec_data is None:
            return (dict(), None, None)
        return (dict(filter(self._goodPair, rec_data.items())),
            rec_data.get('_h'),
            AnfisaConfig.normalizeTime(rec_data.get('_t')))

    def makeRecReport(self, rec_no):
        ret = self.getTagListInfo()
        ret["marker"] = [rec_no, rec_no in self.mMarkedSet]
        rec_tags, history, time_label = self._getRecData(rec_no)
        ret["rec-tags"] = rec_tags
        ret["time"] = time_label
        if history is not None:
            idx_h, len_h = history[0], len(history[1])
            if idx_h > 0:
                ret["can_undo"] = True
            if idx_h + 1 < len_h:
                ret["can_redo"] = True
        return ret

    @classmethod
    def _cloneTagObj(cls, data, time_label = None):
        new_rec_data = dict()
        if data is not None:
            for key, value in data.items():
                if cls._goodPair((key, value)):
                    new_rec_data[key] = value
            if time_label is None and '_t' in data:
                new_rec_data['_t'] = data['_t']
        if time_label is not None:
            new_rec_data['_t'] = time_label
        return new_rec_data

    def _changeRecord(self, rec_no, rec_key, rec_data, tags_to_update):
        if rec_data and rec_data.get('_h') is not None:
            h_idx, h_stack = rec_data['_h']
            h_stack = h_stack[:]
        else:
            h_idx, h_stack = 1, [dict()]
        new_rec_data = None
        if tags_to_update == "UNDO":
            if h_idx > 0:
                if h_idx == len(h_stack):
                    h_stack.append(self._cloneTagObj(rec_data))
                h_idx -= 1
                new_rec_data = self._cloneTagObj(h_stack[h_idx])
                new_rec_data['_h'] = [h_idx, h_stack]
        elif tags_to_update == "REDO":
            if rec_data and rec_data.get('_h') is not None:
                h_idx, h_stack = rec_data['_h']
                if h_idx + 1 < len(h_stack):
                    h_idx += 1
                    new_rec_data = self._cloneTagObj(h_stack[h_idx])
                    new_rec_data['_h'] = [h_idx, h_stack]
        else:
            new_rec_data = self._cloneTagObj(tags_to_update,
                datetime.now().isoformat())
            if ("_note" in new_rec_data and not new_rec_data["_note"].strip()):
                del new_rec_data["_note"]
            h_stack = h_stack[:h_idx + 1]
            if rec_data is not None:
                h_stack.append(self._cloneTagObj(rec_data))
            if len(h_stack) > 10:
                h_stack = h_stack[-10:]
            new_rec_data['_h'] = [len(h_stack), h_stack]
        if new_rec_data is None:
            return
        self.getDS().getSolEnv().setTagsData(
            rec_key, new_rec_data, rec_data)
        tags_prev = set(rec_data.keys() if rec_data is not None else [])
        tags_new  = set(new_rec_data.keys())
        list_modified = False
        for tag_name in tags_prev - tags_new:
            if self._goodKey(tag_name):
                self.mTagSets[tag_name].remove(rec_no)
                if len(self.mTagSets[tag_name]) == 0:
                    del self.mTagSets[tag_name]
                    list_modified = True
        for tag_name in tags_new - tags_prev:
            if self._goodKey(tag_name):
                list_modified |= not self.mTagSets[tag_name]
                self.mTagSets[tag_name].add(rec_no)
        if list_modified:
            self.mIntVersion += 1
        if filter(self._goodKey, new_rec_data.keys()):
            if rec_no not in self.mMarkedSet:
                self.mMarkedSet.add(rec_no)
        else:
            if rec_no in self.mMarkedSet:
                self.mMarkedSet.remove(rec_no)
        return

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
            "tags-version": self.mIntVersion}
        if tag_name:
            rep["records"] = sorted(self.mTagSets[tag_name])
        return rep

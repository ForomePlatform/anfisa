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

from bitarray import bitarray
#===============================================
class ColGroupsH:
    def __init__(self, attr_title_pairs = None,
            attr = None, title = None,  single_columns = False):
        self.mATPairs = attr_title_pairs
        self.mHitGroup = None
        self.mSingleColumns = single_columns
        if attr is not None:
            assert self.mATPairs is None
            self.mATPairs  = [(attr, title)]
            assert not self.mSingleColumns
        else:
            assert self.mATPairs is not None

    def setHitGroup(self, group_attr):
        for idx, pair in enumerate(self.mATPairs):
            if pair[0] == group_attr:
                self.mHitGroup = idx
                return
        assert False, "Failed to set view hit group"

    def getSize(self):
        return len(self.mATPairs)

    def getAttr(self, idx):
        return self.mATPairs[idx][0]

    def getTitle(self, idx):
        return self.mATPairs[idx][1]

    def getAttrNames(self):
        return [attr for attr, title in self.mATPairs]

    def getSingleColumns(self):
        return self.mSingleColumns

    #=============================
    def dump(self):
        ret = [[attr, title] for attr, title in self.mATPairs]
        if self.mSingleColumns:
            ret.append("single_columns")
        return ret

    @classmethod
    def load(cls, data):
        if data is None:
            return None
        attr_title_pairs,  single_columns  = data,  False
        if attr_title_pairs[-1] == "single_columns":
            attr_title_pairs = attr_title_pairs[:-1]
            single_columns = True
        return cls(attr_title_pairs = attr_title_pairs,
            single_columns = single_columns)

    #=============================
    def formColumns(self, in_objects, details = None):
        assert len(in_objects) == 1
        rec_obj = in_objects[0]
        prefix_head = []
        objects = []
        hit_columns = None
        if details and self.mHitGroup is not None:
            hit_columns = set()
        group_idx = -1
        for attr, title in self.mATPairs:
            group_idx += 1
            if attr not in rec_obj:
                continue
            seq = rec_obj[attr]
            if self.mSingleColumns:
                seq = [seq]
            elif len(seq) == 0:
                continue
            rep_count = "[%d]" % len(seq)
            if hit_columns is not None and self.mHitGroup == group_idx:
                it_map = bitarray(details)
                for idx in range(len(seq)):
                    if it_map[idx]:
                        hit_columns.add(idx + len(objects))
                if len(hit_columns) != len(seq):
                    rep_count = "[%d/%d]" % (len(hit_columns), len(seq))
            objects += seq
            if title and not self.mSingleColumns:
                title += rep_count
            prefix_head.append((title, len(seq)))
        if len(prefix_head) == 1 and prefix_head[0][0] is None:
            prefix_head = None
        return objects, prefix_head, hit_columns

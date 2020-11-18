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
from bitarray import bitarray
#===============================================
class ColGroupsH:
    def __init__(self, attr_title_pairs,
            single_group_col = False):
        self.mATPairs = attr_title_pairs
        self.mHitGroup = None
        self.mSingleGroupCol = single_group_col

    def hasSingleGroupCol(self):
        return self.mSingleGroupCol

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

    def getAttrNames(self):
        return [attr for attr, title in self.mATPairs]

    #=============================
    def dump(self):
        ret = [[attr, title] for attr, title in self.mATPairs]
        if self.mSingleGroupCol:
            ret.append("single_group_col")
        return ret

    @classmethod
    def load(cls, data):
        if data is None:
            return None
        attr_title_pairs = data
        if isinstance(attr_title_pairs[-1], str):
            assert attr_title_pairs[-1].startswith("single_")
            attr_title_pairs = attr_title_pairs[:-1]

        return cls(attr_title_pairs = attr_title_pairs)

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
            rep_count = None
            if seq is None or len(seq) == 0:
                continue
            if self.mSingleGroupCol or not isinstance(seq, list):
                seq = [seq]
            else:
                rep_count = "[%d]" % len(seq)
            add_title_class = ""
            if hit_columns is not None:
                if self.mHitGroup == group_idx:
                    it_map = bitarray(details)
                    for idx in range(len(seq)):
                        if it_map[idx]:
                            hit_columns.add(idx + len(objects))
                    if len(hit_columns) != len(seq):
                        rep_count = "[%d/%d]" % (len(hit_columns), len(seq))
                    rep_count += (
                        '&nbsp;<span id="tr-hit-span"></span>')
                else:
                    add_title_class = " no-hit"
            objects += seq
            if title:
                title = escape(title)
            if title and rep_count:
                title += rep_count
            prefix_head.append((title, len(seq), add_title_class))
        if len(prefix_head) == 1 and prefix_head[0][0] is None:
            prefix_head = None
        return objects, prefix_head, hit_columns

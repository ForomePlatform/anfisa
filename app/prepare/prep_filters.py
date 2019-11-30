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

import app.prepare.prep_unit as prep_unit
from app.model.family import FamilyInfo
from app.model.sol_space import SolutionSpace

#===============================================
class FilterPrepareSetH(SolutionSpace):
    def __init__(self, metadata_record,  modes = None):
        SolutionSpace.__init__(self, modes)
        self.mUnits = []
        self.mVGroups  = dict()
        self.mCurVGroup = None
        self.mMeta = metadata_record
        self.mFamilyInfo = FamilyInfo(self.mMeta["samples"],
            self.mMeta.get("proband"))

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def viewGroup(self, view_group_title):
        assert view_group_title not in self.mVGroups
        ret = ViewGroupH(self, view_group_title, len(self.mVGroups))
        self.mVGroups[view_group_title] = ret
        return ret

    def _startViewGroup(self, view_group_h):
        assert self.mCurVGroup is None
        self.mCurVGroup = view_group_h

    def _endViewGroup(self, view_group_h):
        assert self.mCurVGroup is view_group_h
        self.mCurVGroup = None

    def _addUnit(self, unit):
        for conv in self.mUnits:
            assert conv.getName() != unit.getName()
        self.mUnits.append(unit)
        return unit

    def intValueUnit(self, name, path, title = None,
            default_value = None, diap = None, conversion = None,
            render_mode = None, tooltip = None):
        return self._addUnit(prep_unit.IntConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            default_value, diap, conversion))

    def floatValueUnit(self, name, path, title = None,
            default_value = None, diap = None, conversion = None,
            render_mode = None, tooltip = None):
        return self._addUnit(prep_unit.FloatConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            default_value, diap, conversion))

    def statusUnit(self, name, path, title = None,
            variants = None, default_value = "False",
            accept_other_values = False,
            render_mode = None, tooltip = None):
        return self._addUnit(prep_unit.EnumConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            True, variants, default_value,
            accept_other_values = accept_other_values))

    def presenceUnit(self, name, var_info_seq, title = None,
            render_mode = None, tooltip = None):
        return self._addUnit(prep_unit.PresenceConvertor(name, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            var_info_seq))

    def multiStatusUnit(self, name, path, title = None,
            variants = None, default_value = None,
            separators = None, compact_mode = False,
            accept_other_values = False, render_mode = None, tooltip = None,
            conversion = None):
        return self._addUnit(prep_unit.EnumConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            False, variants, default_value,
            separators = separators, compact_mode = compact_mode,
            accept_other_values = accept_other_values,
            conv_func = conversion))

    def zygositySpecialUnit(self, name, path, title = None,
            default_value = None, config = None,
            render_mode = None, tooltip = None,):
        return self._addUnit(prep_unit.ZygosityConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip, config, self))

    def panelStatusUnit(self, name, unit_base, title = None,
            render_mode = None, tooltip = None,
            view_path = None):
        return self._addUnit(prep_unit.PanelConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip, unit_base, view_path))

    def transctiptStatusUnit(self, name, trans_name,
            title = None, render_mode = None, tooltip = None,
            variants = None, default_value = "False", bool_check_value = None):
        return self._addUnit(prep_unit.TransctiptConvertor(
            name, title, len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip, "transcript-status", trans_name, variants,
            default_value, bool_check_value))

    def transctiptMultisetUnit(self, name, trans_name,
            title = None, render_mode = None, tooltip = None,
            variants = None):
        return self._addUnit(prep_unit.TransctiptConvertor(
            name, title, len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip,
            "transcript-multiset", trans_name, variants))

    def process(self, rec_no, rec_data):
        result = dict()
        for unit in self.mUnits:
            unit.process(rec_no, rec_data, result)
        return result

    def reportProblems(self, output):
        for unit in self.mUnits:
            if unit.getErrorCount() > 0:
                print("Field %s: %d bad conversions" % (
                    unit.getName(), unit.getErrorCount()), file = output)
        return True

    def dump(self):
        return [unit.dump() for unit in self.mUnits]

    def getTranscriptDescrSeq(self):
        ret = []
        for unit in self.mUnits:
            descr = unit.getTranscriptDescr()
            if descr is not None:
                ret.append(descr)
        return ret

#===============================================
class ViewGroupH:
    def __init__(self, filter_set, title, no):
        self.mFilterSet = filter_set
        self.mTitle = title
        self.mNo = no
        self.mUnits = []

    def __enter__(self):
        self.mFilterSet._startViewGroup(self)
        return self

    def __exit__(self, tp, value, traceback):
        self.mFilterSet._endViewGroup(self)

    def addUnit(self, unit):
        self.mUnits.append(unit)

    def getTitle(self):
        return self.mTitle

    def getUnits(self):
        return self.mUnits

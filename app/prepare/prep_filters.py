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

from forome_tools.path_works import AttrFuncPool
from forome_tools.ident import checkIdentifier
from app.config.a_config import AnfisaConfig
import app.prepare.prep_unit as prep_unit
from app.model.family import FamilyInfo
from app.model.sol_broker import SolutionBroker
#===============================================
class FilterPrepareSetH(SolutionBroker):

    sZygosityPath = AnfisaConfig.configOption("zygosity.path.base")
    sNamedFunctions = dict()

    def __init__(self, metadata_record,  modes = None,
            check_identifiers = True):
        SolutionBroker.__init__(self,
            metadata_record.get("data_schema", "CASE"), modes)
        self.mUnits = []
        self.mVGroups  = dict()
        self.mCurVGroup = None
        self.mMeta = metadata_record
        self.mFamilyInfo = FamilyInfo(self.mMeta)
        self.mCheckIdent = check_identifiers
        self.mPreTransformSeq = []

        assert self.sZygosityPath is not None
        self.mZygosityData = ZygosityDataPreparator(
            "_zyg", self.sZygosityPath, self.mFamilyInfo)

    @classmethod
    def regNamedFunction(cls, name, func):
        assert name not in cls.sNamedFunctions
        cls.sNamedFunctions[name] = func

    @classmethod
    def getNamedFunction(cls, name):
        return cls.sNamedFunctions.get(name)

    def setupFromInfo(self, info_seq):
        for info in info_seq:
            self._setViewGroup(info.get("vgroup"))
            unit_h = prep_unit.loadConvertorInstance(info,
                self.mCurVGroup, self)
            self._addUnit(unit_h)
        self._setViewGroup(None)

    def getFamilyInfo(self):
        return self.mFamilyInfo

    def viewGroup(self, view_group_title):
        assert view_group_title not in self.mVGroups, (
            "View group duplication: " + view_group_title)
        ret = ViewGroupH(self, view_group_title, len(self.mVGroups))
        self.mVGroups[view_group_title] = ret
        return ret

    def checkUnitName(self, name):
        if self.mCheckIdent:
            assert checkIdentifier(name), "Bad unit name: " + name

    def regPreTransform(self, transform_f):
        self.mPreTransformSeq.append(transform_f)

    def _startViewGroup(self, view_group_h):
        assert self.mCurVGroup is None
        self.mCurVGroup = view_group_h

    def _endViewGroup(self, view_group_h):
        assert self.mCurVGroup is view_group_h
        self.mCurVGroup = None

    def _setViewGroup(self, view_group_title):
        if view_group_title is None:
            self.mCurVGroup = None
        elif (self.mCurVGroup is None
                or self.mCurVGroup.getTitle() != view_group_title):
            self.mCurVGroup = self.viewGroup(view_group_title)

    def _addUnit(self, unit_h):
        self.checkUnitName(unit_h.getName())
        for conv in self.mUnits:
            assert conv.getName() != unit_h.getName()
        self.mUnits.append(unit_h)
        return unit_h

    def intValueUnit(self, name, vpath, title = None,
            default_value = None, diap = None,
            conversion = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.IntConvertor(self,
            name, vpath, title, len(self.mUnits), self.mCurVGroup,
            default_value, diap, conversion, render_mode, tooltip))

    def floatValueUnit(self, name, vpath, title = None,
            default_value = None, diap = None,
            conversion = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.FloatConvertor(self,
            name, vpath, title, len(self.mUnits), self.mCurVGroup,
            default_value, diap, conversion, render_mode, tooltip))

    def statusUnit(self, name, vpath, title = None,
            variants = None, default_value = "False",
            accept_other_values = False, value_map = None,
            conversion = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.EnumConvertor(self,
            name, vpath, title, len(self.mUnits), self.mCurVGroup,
            "status", variants, accept_other_values, value_map,
            conversion, render_mode, tooltip,
            default_value = default_value))

    def multiStatusUnit(self, name, vpath, title = None,
            variants = None, default_value = None,
            compact_mode = False,
            accept_other_values = False, value_map = None,
            conversion = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.EnumConvertor(self,
            name, vpath, title, len(self.mUnits), self.mCurVGroup,
            "multi", variants, accept_other_values, value_map,
            conversion, render_mode, tooltip,
            compact_mode = compact_mode,
            default_value = default_value))

    def presenceUnit(self, name, var_info_seq, title = None,
            render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.PresenceConvertor(self, name, title,
            len(self.mUnits), self.mCurVGroup, var_info_seq,
            render_mode, tooltip))

    def panelsUnit(self, name, unit_base, panel_type, title = None,
            render_mode = None, tooltip = None, view_path = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.PanelConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            unit_base, panel_type, view_path, render_mode, tooltip))

    def transcriptIntValueUnit(self, name, trans_name, title = None,
            default_value = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        assert default_value is not None, (
            "Transcript Int unit %s requires default" % name)
        return self._addUnit(prep_unit.TranscriptNumConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            "transcript-int", trans_name, default_value,
            render_mode, tooltip))

    def transcriptFloatValueUnit(self, name, trans_name, title = None,
            default_value = None, render_mode = None, tooltip = None):
        self.checkUnitName(name)
        assert default_value is not None, (
            "Transcript Float unit %s requires default" % name)
        return self._addUnit(prep_unit.TranscriptNumConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            "transcript-float", trans_name, default_value,
            render_mode, tooltip,))

    def transcriptStatusUnit(self, name, trans_name, title = None,
            variants = None, default_value = "False",
            render_mode = None, tooltip = None, bool_check_value = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.TranscriptEnumConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            "transcript-status", trans_name, variants, default_value,
            render_mode, tooltip, bool_check_value))

    def transcriptMultisetUnit(self, name, trans_name, title = None,
            variants = None, default_value = None,
            render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.TranscriptEnumConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            "transcript-multiset", trans_name, variants, default_value,
            render_mode, tooltip))

    def transcriptPanelsUnit(self, name, unit_base, panel_type,
            title = None, view_name = None,
            render_mode = None, tooltip = None):
        self.checkUnitName(name)
        return self._addUnit(prep_unit.TranscriptPanelsConvertor(self,
            name, title, len(self.mUnits), self.mCurVGroup,
            unit_base, panel_type, view_name,
            render_mode, tooltip))

    def process(self, rec_no, rec_data):
        for transform_f in self.mPreTransformSeq:
            transform_f(rec_no, rec_data)
        result = dict()
        for unit in self.mUnits:
            unit.process(rec_no, rec_data, result)
        self.mZygosityData.process(rec_no, rec_data, result)
        return result

    def reportProblems(self, output):
        for unit in self.mUnits:
            if unit.getErrorCount() > 0:
                print("Field %s: %d bad conversions" % (
                    unit.getName(), unit.getErrorCount()), file = output)
        return True

    def dump(self):
        return [unit.dump() for unit in self.mUnits]

    def getZygosityNames(self):
        return self.mZygosityData.getMemberNames()

    def getZygosityVarName(self):
        return self.mZygosityData.getVarName()

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

#===============================================
class ZygosityDataPreparator:
    def __init__(self, var_name, vpath, family_info):
        self.mVarName = var_name
        self.mPath   = vpath
        self.mPathF  = AttrFuncPool.makeFunc(self.mPath)
        assert family_info is not None, "No dataset metadata with samples info"
        self.mMemberIds = [id
            for id in family_info.getIds()]
        self.mMemberNames = ["%s_%d" % (var_name, idx)
            for idx in range(len(self.mMemberIds))]

    def getVarName(self):
        return self.mVarName

    def getMemberNames(self):
        return self.mMemberNames

    def process(self, rec_no, rec_data, result):
        zyg_distr_seq = self.mPathF(rec_data)
        if not zyg_distr_seq:
            assert len(self.mMemberNames) == 0
            return
        assert len(zyg_distr_seq) == 1
        zyg_distr = zyg_distr_seq[0]
        assert len(zyg_distr.keys()) == len(self.mMemberNames)
        for idx, member_id in enumerate(self.mMemberIds):
            zyg_val = zyg_distr[member_id]
            if zyg_val is None:
                zyg_val = -1
            result[self.mMemberNames[idx]] = zyg_val

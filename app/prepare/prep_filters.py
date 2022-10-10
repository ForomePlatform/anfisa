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
from app.model.sol_broker import SolutionBroker
#===============================================
class FilterPrepareSetH(SolutionBroker):

    sZygosityPath = AnfisaConfig.configOption("zygosity.path.base")
    sNamedFunctions = dict()

    def __init__(self, metadata_record, var_registry, ds_kind,
            derived_mode = False, check_identifiers = True,
            druid_adm = None, pre_flt_schema = None):
        SolutionBroker.__init__(self, metadata_record, ds_kind,
            derived_mode = derived_mode, zygosity_support = True)

        self.mVarRegistry = var_registry
        self.mUnits = []
        self.mVGroups  = dict()
        self.mCurVGroup = None
        self.mMeta = metadata_record
        self.mCheckIdent = check_identifiers
        self.mPreTransformSeq = []
        self.mTranscriptIdName = None
        self.mDruidAdm = druid_adm

        self.mTransPathBaseF = AttrFuncPool.makeFunc(
            AnfisaConfig.configOption("transcript.path.base"))

        assert self.sZygosityPath is not None, (
            "Missing configuration zygosity.path.base setting")
        self.mZygosityData = ZygosityDataPreparator(
            "_zyg", self.sZygosityPath, self.getFamilyInfo())

        if pre_flt_schema is not None:
            self._setupSchema(pre_flt_schema)

    @classmethod
    def regNamedFunction(cls, name, func):
        assert name not in cls.sNamedFunctions, (
            "Function name duplication: " + name)
        cls.sNamedFunctions[name] = func

    @classmethod
    def getNamedFunction(cls, name):
        return cls.sNamedFunctions.get(name)

    def _setupSchema(self, info_seq):
        for info in info_seq:
            self._setViewGroup(info.get("vgroup"))
            unit_h = prep_unit.loadConvertorInstance(info,
                self.mCurVGroup, self)
            self._addUnit(unit_h)
            if unit_h.isTranscriptID():
                assert self.mTranscriptIdName is None, (
                    "Transcript ID unit duplication: " + unit_h.getName()
                    + " | " + self.mTranscriptIdName)
                self.mTranscriptIdName = unit_h.getName()
        self._setViewGroup(None)

    def getTranscriptIdUnitName(self):
        return self.mTranscriptIdName

    def viewGroup(self, view_group_title):
        assert view_group_title not in self.mVGroups, (
            "View group duplication: " + view_group_title)
        ret = ViewGroupH(self, view_group_title, len(self.mVGroups))
        self.mVGroups[view_group_title] = ret
        return ret

    def _checkVar(self, name, var_type):
        if self.mCheckIdent:
            assert checkIdentifier(name), "Bad unit name: " + name
        var_tp, _ = self.mVarRegistry.getVarInfo(name)
        assert var_tp == var_type, (
            f"Bad check type for {name}: {var_tp} vs. {var_type}")

    def regPreTransform(self, transform_f):
        self.mPreTransformSeq.append(transform_f)

    def _startViewGroup(self, view_group_h):
        assert self.mCurVGroup is None, "View group is currently pushed"
        self.mCurVGroup = view_group_h

    def _endViewGroup(self, view_group_h):
        assert self.mCurVGroup is view_group_h, "View group conflict"
        self.mCurVGroup = None

    def _setViewGroup(self, view_group_title):
        if view_group_title is None:
            self.mCurVGroup = None
        elif (self.mCurVGroup is None
                or self.mCurVGroup.getTitle() != view_group_title):
            self.mCurVGroup = self.viewGroup(view_group_title)

    def _addUnit(self, unit_h):
        for u_h in self.mUnits:
            assert u_h.getName() != unit_h.getName(), (
                "Unit name collision" + u_h.getName())
        self.mUnits.append(unit_h)
        return unit_h

    def intValueUnit(self, name, vpath, default_value = None,
            diap = None, conversion = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "numeric")
        return self._addUnit(prep_unit.IntConvertor(self,
            name, vpath, len(self.mUnits), self.mCurVGroup,
            default_value, diap, conversion))

    def floatValueUnit(self, name, vpath, default_value = None,
            diap = None, conversion = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "numeric")
        return self._addUnit(prep_unit.FloatConvertor(self,
            name, vpath, len(self.mUnits), self.mCurVGroup,
            default_value, diap, conversion))

    def statusUnit(self, name, vpath,
            variants = None, default_value = "False",
            value_map = None, conversion = None,
            dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        return self._addUnit(prep_unit.EnumConvertor(self,
            name, vpath, len(self.mUnits), self.mCurVGroup, dim_name,
            "status", variants, value_map,
            conversion, default_value = default_value))

    def multiStatusUnit(self, name, vpath,
            variants = None, default_value = None, compact_mode = False,
            value_map = None, conversion = None,
            dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        return self._addUnit(prep_unit.EnumConvertor(self,
            name, vpath, len(self.mUnits), self.mCurVGroup, dim_name,
            "multi", variants, value_map,
            conversion, compact_mode = compact_mode,
            default_value = default_value))

    def presenceUnit(self, name, var_info_seq, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        return self._addUnit(prep_unit.PresenceConvertor(self, name,
            len(self.mUnits), self.mCurVGroup, var_info_seq))

    def varietyUnit(self, name, variety_name, panel_name, vpath, panel_type,
            requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        self._checkVar(panel_name, "enum")
        self._checkVar(variety_name, "enum")
        return self._addUnit(prep_unit.VarietyConvertor(self, name,
            len(self.mUnits), self.mCurVGroup,
            variety_name, panel_name, vpath, panel_type))

    # reserved (currently out of use)
    def panelsUnit(self, name, unit_base, panel_type,
            view_path = None, dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        return self._addUnit(prep_unit.PanelConvertor(self,
            name, len(self.mUnits), self.mCurVGroup, dim_name,
            unit_base.getName(), panel_type, view_path))

    def transcriptIntValueUnit(self, name, trans_name,
            default_value = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "numeric")
        assert default_value is not None, (
            f"Transcript Int unit {name} requires default")
        return self._addUnit(prep_unit.TranscriptNumConvertor(self,
            name, len(self.mUnits), self.mCurVGroup,
            "transcript-int", trans_name, default_value))

    def transcriptFloatValueUnit(self, name, trans_name,
            default_value = None, dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "numeric")
        assert default_value is not None, (
            f"Transcript Float unit {name} requires default")
        return self._addUnit(prep_unit.TranscriptNumConvertor(self,
            name, len(self.mUnits), self.mCurVGroup, dim_name,
            "transcript-float", trans_name, default_value))

    def transcriptStatusUnit(self, name, trans_name,
            variants = None, default_value = "False",
            bool_check_value = None, transcript_id_mode = False,
            dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        if transcript_id_mode:
            assert self.mTranscriptIdName is None, (
                "Transcript ID unit set twice: " + self.mTranscriptIdName
                + " | " + name)
            self.mTranscriptIdName = name
        return self._addUnit(prep_unit.TranscriptStatusConvertor(self,
            name, len(self.mUnits), self.mCurVGroup, dim_name,
            "transcript-status", trans_name, variants, default_value,
            bool_check_value, transcript_id_mode))

    def transcriptMultisetUnit(self, name, trans_name, variants = None,
            default_value = None, dim_name = None, requires = None):
        if requires and not self.testRequirements(requires):
            return None
        self._checkVar(name, "enum")
        return self._addUnit(prep_unit.TranscriptMultiConvertor(self,
            name, len(self.mUnits), self.mCurVGroup, dim_name,
            "transcript-multiset", trans_name, variants, default_value))

    def transcriptVarietyUnit(self, name, panel_name, trans_name, panel_type,
            default_value = None, requires = None):
        self._checkVar(name, "enum")
        self._checkVar(panel_name, "enum")
        if requires and not self.testRequirements(requires):
            return None
        return self._addUnit(prep_unit.TranscriptVarietyConvertor(self,
            name, len(self.mUnits), self.mCurVGroup,
            trans_name, panel_type, panel_name, default_value))

    # reserved (currently out of use)
    def transcriptPanelsUnit(self, name, unit_base, panel_type,
            view_name = None, dim_name = None, requires = None):
        self._checkVar(name, "enum")
        if requires and not self.testRequirements(requires):
            return None
        return self._addUnit(prep_unit.TranscriptPanelsConvertor(self,
            name, len(self.mUnits), self.mCurVGroup, dim_name,
            unit_base.getTranscriptName(), panel_type, view_name))

    def process(self, rec_no, rec_data, pre_data):
        for transform_f in self.mPreTransformSeq:
            transform_f(rec_no, rec_data)

        ws_mode = (self.getDSKind() == "ws")

        result = dict()
        tr_seq_seq = self.mTransPathBaseF(rec_data)
        assert len(tr_seq_seq) <= 1
        if len(tr_seq_seq) == 1:
            tr_seq = tr_seq_seq[0]
        else:
            tr_seq = []
        if ws_mode:
            result["$1"] = len(tr_seq)

        for unit_h in self.mUnits:
            if unit_h.getTranscriptName() is None:
                unit_h.process(rec_no, rec_data, result)
                continue

            if len(tr_seq) == 0:
                unit_h.processEmpty()
                continue

            tr_name = unit_h.getTranscriptName()
            res_seq = [unit_h.processOne(tr_obj.get(tr_name))
                for tr_obj in tr_seq]
            if ws_mode:
                result[unit_h.getName()] = res_seq
            assert unit_h.isOK(), (
                f"Tr-unit {unit_h.getName()} improper evaluation")

        self.mZygosityData.process(rec_no, rec_data, result)
        if self.mDruidAdm is not None:
            result.update(self.mDruidAdm.internalFltData(
                rec_no, pre_data))
        return result

    def reportProblems(self, output):
        for unit in self.mUnits:
            if unit.getErrorCount() > 0:
                print(f"Field {unit.getName()}: "
                    f"{unit.getErrorCount()} bad conversions", file = output)
        return True

    def dump(self):
        return [unit.dump() for unit in self.mUnits]

    def getZygosityNames(self):
        return self.mZygosityData.getMemberNames()

    def getZygosityVarName(self):
        return self.mZygosityData.getVarName()

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
        self.mMemberNames = [f"{var_name}_{idx}"
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

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
import logging
from zlib import crc32
from forome_tools.path_works import AttrFuncPool, AttrFuncHelper
from forome_tools.ident import checkIdentifier
from app.config.a_config import AnfisaConfig
from app.config import getDS_Schema
import app.prepare.prep_unit as prep_unit
from app.model.sol_broker import SolutionBroker

#===============================================
class FiltersMaster(SolutionBroker):

    sNamedFunctions = dict()

    def __init__(self, metadata_record, ds_kind,
            derived_mode = False,
            druid_adm = None,
            pre_flt_schema = None,
            path_base = None):
        SolutionBroker.__init__(self, metadata_record, ds_kind,
            derived_mode = derived_mode, zygosity_support = True)

        self.mVarRegistry = getDS_Schema(metadata_record).defineVariables(
                self, metadata_record, ds_kind)
        self.mUnits = []
        self.mVGroups  = dict()
        self.mCurVGroup = None
        self.mMeta = metadata_record
        self.mPreTransformSeq = []
        self.mTranscriptIdName = None
        self.mDruidAdm = druid_adm
        self.mPathBase = (path_base if path_base is not None
            else AnfisaConfig.sDefaultPathBase)

        self.mTransPathBaseF = AttrFuncPool.makeFunc(self._getPathBase("transcripts"))

        self.mZygosityData = ZygosityDataPreparator(
            "_zyg", self._getPathBase("zygosity"), self.getFamilyInfo())
        self.mSysFieldsGetter = None

        self.mTranscriptIdName = None

        if pre_flt_schema is not None:
            self._setupSecondarySchema(pre_flt_schema)

    @classmethod
    def regNamedFunction(cls, name, func):
        assert name not in cls.sNamedFunctions, (
            "Function name duplication: " + name)
        cls.sNamedFunctions[name] = func

    @classmethod
    def getNamedFunction(cls, name):
        return cls.sNamedFunctions.get(name)

    def getVarRegistry(self):
        return self.mVarRegistry

    def _getPathBase(self, name):
        path_val = self.mPathBase.get(name)
        assert path_val is not None, (
            "Missing configuration path path base for " + name)
        return path_val

    def _setupSecondarySchema(self, info_seq):
        for info in info_seq:
            self.startViewGroup(info.get("vgroup"))
            unit_h = prep_unit.loadConvertorInstance(info,
                self.mCurVGroup, self)
            self._addUnit(unit_h)
        self.standUp()

    def getTranscriptIdUnitName(self):
        return self.mTranscriptIdName

    def startViewGroup(self, view_group_title):
        if self.mCurVGroup and view_group_title == self.mCurVGroup.getTitle():
            return
        assert view_group_title not in self.mVGroups, (
            "View group duplication: " + view_group_title)
        self.mCurVGroup = ViewGroupH(self, view_group_title, len(self.mVGroups))
        self.mVGroups[view_group_title] = self.mCurVGroup

    def standUp(self):
        assert self.mTranscriptIdName is not None, (
            "Transcript ID unit is not set")
        self.mCurVGroup = None


    sConflictsAllowed = [
        ("panel", "multiset"),
        ("multiset", "variety"),
        ("status", "variety")]

    def getVarDescr(self, name, var_type=None, transcript_mode=False):
        assert checkIdentifier(name), "Bad unit name: " + name
        if name not in self.mVarRegistry:
            logging.error("No variable: " + name)
            return None
        var_descr = self.mVarRegistry[name]
        if var_type is not None and var_type != var_descr["type"]:
            var_type1 = var_descr["type"]
            for t1, t2 in self.sConflictsAllowed:
                if t1 == var_type and t2 == var_type1:
                    var_type1 = None
                    break
            if var_type1 is not None:
                logging.error(
                    f"Variable {name} type conflict: {var_type}/{var_type1}")
                return None
        if (var_descr.get("requires") and
                not self.testRequirements(var_descr["requires"])):
            return None
        tr_mode = var_descr.get("transcript-mode")
        assert (not transcript_mode) == (not tr_mode), (
            f"Variable {name} transcript-mode conflict: {tr_mode}/" +
            f"{transcript_mode}")
        return var_descr

    def regPreTransform(self, transform_f):
        self.mPreTransformSeq.append(transform_f)

    def _addUnit(self, unit_h):
        for u_h in self.mUnits:
            assert u_h.getName() != unit_h.getName(), (
                "Unit name collision " + u_h.getName())
        self.mUnits.append(unit_h)
        if unit_h.getVarDescr().get("transcript-mode") == "master":
            assert self.mTranscriptIdName is None, (
                "Transcript ID duplication: " + self.mTranscriptIdName +
                " vs " + unit_h.getName())
            self.mTranscriptIdName = unit_h.getName()
        return unit_h

    def intValueUnit(self, name, vpath, conversion = None):
        var_descr = self.getVarDescr(name, "int")
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.IntConvertor(self, var_descr,
            vpath, len(self.mUnits), self.mCurVGroup,
            var_descr.get("default"), var_descr.get("diap"), conversion))

    def floatValueUnit(self, name, vpath, conversion = None):
        var_descr = self.getVarDescr(name, "float")
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.FloatConvertor(self, var_descr,
            vpath, len(self.mUnits), self.mCurVGroup,
            var_descr.get("default"), var_descr.get("diap"), conversion))

    def statusUnit(self, name, vpath, conversion = None):
        var_descr = self.getVarDescr(name, "status")
        if var_descr is None:
            return None
        # dim-name is reserved
        return self._addUnit(prep_unit.EnumConvertor(self, var_descr,
            vpath, len(self.mUnits), self.mCurVGroup,
            var_descr.get("dim-name"), "status",
            var_descr.get("variants"), var_descr.get("value-map"),
            conversion,
            default_value = var_descr.get("default")))

    def multiStatusUnit(self, name, vpath, compact_mode = False,
            conversion = None):
        var_descr = self.getVarDescr(name, "multiset")
        if var_descr is None:
            return None
        # dim-name is reserved
        return self._addUnit(prep_unit.EnumConvertor(self, var_descr,
            vpath, len(self.mUnits), self.mCurVGroup,
            var_descr.get("dim-name"), "multi",
            var_descr.get("variants"), var_descr.get("value-map"),
            conversion, compact_mode = compact_mode,
            default_value = var_descr.get("default")))

    def presenceUnit(self, name, var_info_seq = None):
        var_descr = self.getVarDescr(name, "presence")
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.PresenceConvertor(self, var_descr,
            len(self.mUnits), self.mCurVGroup, var_info_seq))

    def varietyUnit(self, name, variety_name, vpath):
        var_descr = self.getVarDescr(variety_name, "variety")
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.VarietyConvertor(self, var_descr,
            len(self.mUnits), self.mCurVGroup,
            name, variety_name, var_descr["panel"],
            vpath, var_descr["panel-type"]))

    def panelsUnit(self, unit_base, view_path):
        return self._addUnit(prep_unit.PanelConvertor(self,
            {"attribute": unit_base.getVarDescr()["panel"], "base": unit_base},
            len(self.mUnits), self.mCurVGroup,
            unit_base.getVarDescr().get("dim-name"),
            unit_base.getName(),
            unit_base.getVarDescr()["panel-type"], view_path))

    def transcriptIntValueUnit(self, name, trans_name):
        var_descr = self.getVarDescr(name, "int", transcript_mode=True)
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.TranscriptNumConvertor(self, var_descr,
            len(self.mUnits), self.mCurVGroup,
            "transcript-int", trans_name, var_descr["default"]))

    def transcriptFloatValueUnit(self, name, trans_name):
        var_descr = self.getVarDescr(name, "float", transcript_mode=True)
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.TranscriptNumConvertor(self, var_descr,
            len(self.mUnits), self.mCurVGroup,
            var_descr.get("dim-name"),
            "transcript-int", trans_name, var_descr["default"]))

    def transcriptStatusUnit(self, name, trans_name,
            bool_check_value = None):
        var_descr = self.getVarDescr(name, "status", transcript_mode=True)
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.TranscriptStatusConvertor(self,
            var_descr, len(self.mUnits), self.mCurVGroup,
            var_descr.get("dim-name"),
            "transcript-status", trans_name,
            var_descr.get("variants"), var_descr.get("default"),
            bool_check_value))

    def transcriptMultisetUnit(self, name, trans_name):
        var_descr = self.getVarDescr(name, "multiset", transcript_mode=True)
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.TranscriptMultiConvertor(self,
            var_descr, len(self.mUnits), self.mCurVGroup,
            var_descr.get("dim-name"),
            "transcript-multiset", trans_name,
            var_descr.get("variants"), var_descr.get("default")))

    def transcriptVarietyUnit(self, name, trans_name):
        var_descr = self.getVarDescr(name, "variety", transcript_mode=True)
        if var_descr is None:
            return None
        return self._addUnit(prep_unit.TranscriptVarietyConvertor(self,
            var_descr, len(self.mUnits), self.mCurVGroup,
            trans_name, var_descr["panel-type"], var_descr["panel"],
            var_descr.get("default")))

    def transcriptPanelsUnit(self, unit_base, trans_name = None):
        assert unit_base.getVarDescr().get("transcript-mode"), (
            "Base should be transcript")
        return self._addUnit(prep_unit.TranscriptPanelsConvertor(self,
            {"attribute": unit_base.getVarDescr()["panel"], "base": unit_base},
            len(self.mUnits), self.mCurVGroup,
            unit_base.getVarDescr().get("dim-name"),
            unit_base.getName(),
            unit_base.getVarDescr()["panel-type"], trans_name))

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
                result[unit_h.getInternalName()] = res_seq
            assert unit_h.isOK(), (
                f"Unit {unit_h.getName()} improper evaluation")

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

    def preparePData(self, rec_data):
        if self.mSysFieldsGetter is None:
            self.mSysFieldsGetter = {
                "_color": AttrFuncHelper.singleGetter(
                    self._getPathBase("color")),
                "_label": AttrFuncHelper.singleGetter(
                    self._getPathBase("label")),
                "_key":   AttrFuncHelper.multiStrGetter(
                    "-", [self._getPathBase(key)
                    for key in ("chromosome", "start", "ref", "alt")])}
        result = dict()
        for name, fld_f in self.mSysFieldsGetter.items():
            result[name] = fld_f(rec_data)
        result["_rand"] = crc32(bytes(result["_key"], 'utf-8'))
        return result



#===============================================
class ViewGroupH:
    def __init__(self, filter_set, title, no):
        self.mFilterSet = filter_set
        self.mTitle = title
        self.mNo = no
        self.mUnits = []

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
        if isinstance(zyg_distr, dict):
            assert len(zyg_distr.keys()) == len(self.mMemberNames)
            for idx, member_id in enumerate(self.mMemberIds):
                zyg_val = zyg_distr[member_id]
                if zyg_val is None:
                    zyg_val = -1
                result[self.mMemberNames[idx]] = zyg_val
        else:
            assert len(zyg_distr) == len(self.mMemberNames)
            for idx, zyg_val in enumerate(zyg_distr):
                result[self.mMemberNames[idx]] = zyg_val

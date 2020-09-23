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
import json

from forome_tools.types import Types, TypeCounter
from app.view.attr import AttrH

#===============================================
class AttrTypeChecker:
    sMAX_BAD_COUNT = 3

    def __init__(self, name, base_attr = None, expect_type = None):
        self.mName = name
        self.mBaseAttr = base_attr
        self.mErrors = []
        self.mErrCount = 0
        self.mDetType = False
        self.mStatus = None
        if base_attr:
            expect_type = Types.filterTypeKind(base_attr.getKinds())

        if base_attr and base_attr.isSeq():
            self.mMainTpCnt = TypeCounter("list")
            self.mSubTpCnt = TypeCounter(expect_type)
        else:
            self.mMainTpCnt = TypeCounter(expect_type)
            self.mSubTpCnt = TypeCounter()

    def setStatus(self, status):
        self.mStatus = status

    def getName(self):
        return self.mName

    def getKind(self):
        return "Attr"

    def getBaseAttr(self):
        return self.mBaseAttr

    def getErrorCount(self):
        return self.mErrCount

    def getDetType(self):
        return self.mDetType

    def regValue(self, rec_no, value):
        assert self.mDetType is False
        is_ok = self.mMainTpCnt.regValue(value)
        if is_ok and isinstance(value, list):
            for it_val in value:
                is_ok &= self.mSubTpCnt.regValue(it_val)
        if not is_ok:
            self.mErrCount += 1
            if len(self.mErrors) < self.sMAX_BAD_COUNT:
                self.mErrors.append([rec_no, value])
        return is_ok

    def fixType(self, no_mode = False):
        assert self.mDetType is False
        tp = self.mMainTpCnt.detect(no_mode = no_mode)
        if tp == "undef":
            self.mDetType = None
        elif tp == "list":
            self.mDetType = [True, self.mSubTpCnt.detect(no_mode = no_mode)]
            if self.mDetType[1] == "dict":
                self.mDetType[1] = "json"
        else:
            if tp == "dict":
                tp = "json"
            self.mDetType = [False, tp]
        return self.mDetType

    def dump(self):
        return {
            "name": self.mName,
            "detected": self.mDetType,
            "status": self.mStatus,
            "errors": [self.mErrCount, self.mErrors]}

#===============================================
class DictTypeChecker:
    def __init__(self, name, master_name, base_asp = None):
        self.mName = name
        self.mChildren = []
        self.mReg = dict()
        self.mMasterName = master_name
        self.mBaseAsp = base_asp
        self.mOwnCnt = AttrTypeChecker("=", expect_type = "dict")
        self.mStatus = None

    def getName(self):
        return self.mName

    def getKind(self):
        return "Dict"

    def getMasterName(self):
        return self.mMasterName

    def addAttr(self, attr_h):
        if attr_h.getName() is None:
            return
        attr_tp_h = AttrTypeChecker(attr_h.getName(), attr_h)
        self.regIt(attr_tp_h)

    def getReg(self, name):
        return self.mReg.get(name)

    def regIt(self, reg, name = None):
        if name is None:
            name = reg.getName()
        assert name not in self.mReg
        self.mReg[name] = reg
        if len(self.mChildren) == 0 or self.mChildren[-1] is not reg:
            self.mChildren.append(reg)

    def regValue(self, rec_no, value):
        if not self.mOwnCnt.regValue(rec_no, value):
            self.mStatus = "bad"
            return
        for name, val in value.items():
            self.regItemValue(rec_no, name, val)

    def regItemValue(self, rec_no, name, val):
        reg_h = self.mReg.get(name)
        if reg_h is None:
            reg_h = AttrTypeChecker(name)
            self.regIt(reg_h)
        reg_h.regValue(rec_no, val)

    def fixUp(self, master, rep_output, no_mode = False):
        self.mOwnCnt.fixType(no_mode = no_mode)
        if self.mOwnCnt.getErrorCount() > 0:
            master.problem("fatal", self)
            self.mStatus = "fatal"
        else:
            self.mStatus = "ok"
        for a_check in self.mChildren:
            if not isinstance(a_check, AttrTypeChecker):
                a_check.fixUp(master, rep_output, no_mode = no_mode)
                continue
            a_type = a_check.fixType(no_mode = no_mode)
            if a_check.getBaseAttr() is None:
                if a_check.getName().startswith('_'):
                    a_check.setStatus("skipped")
                    continue
                a_seq, a_kind = a_type
                assert a_type is not None
                if self.mBaseAsp:
                    self.mBaseAsp.addAttr(
                        AttrH(a_check.getName(), a_kind, is_seq = a_seq))
                    master.problem("added", a_check, self)
                    a_check.setStatus("added")
                else:
                    master.problem("lost", a_check, self)
                    a_check.setStatus("lost")
            else:
                if self.mBaseAsp is None:
                    # lack of accuracy
                    continue
                attr_h = a_check.getBaseAttr()
                if a_type is None:
                    if (not attr_h.hasKind("place")
                            and not attr_h.hasKind("posted")):
                        self.mBaseAsp.delAttr(attr_h)
                        master.problem("empty", a_check, self)
                    a_check.setStatus("empty")
                else:
                    a_seq, a_kind = a_type
                    if (a_check.getErrorCount() > 0
                            or a_seq != attr_h.isSeq()):
                        print("Update field %s.%s:" %
                            (self.mName, a_check.getName()),
                            attr_h.getMainKind(), "is_seq=", attr_h.isSeq(),
                            "->", a_kind, "is_seq=", a_seq,
                            "errors=", a_check.getErrorCount(),
                            file = rep_output)
                        attr_h.reset(a_kind, a_seq)
                        master.problem("updated", a_check, self)
                        a_check.setStatus("updated")
                    else:
                        a_check.setStatus("ok")

    def dump(self):
        return {
            "name": self.mName,
            "kind": self.getKind(),
            "status": self.mStatus,
            "children": [a_check.dump() for a_check in self.mChildren]}

#===============================================
class ColGroupTypeChecker(DictTypeChecker):
    def __init__(self, name, master_name, base_asp, single_group_col):
        DictTypeChecker.__init__(self, name, master_name, base_asp = base_asp)
        self.mSingleGroupCol = single_group_col

    def getKind(self):
        return "Columns"

    def regValue(self, rec_no, value):
        if self.mSingleGroupCol:
            DictTypeChecker.regValue(self, rec_no, value)
        else:
            if value is None:
                return
            assert isinstance(value, list), (
                "Not a list " + self.getMasterName() + "/" + self.getName()
                + "\n" + json.dumps(value))
            for it in value:
                DictTypeChecker.regValue(self, rec_no, it)

#===============================================
class SourceTypeChecker(DictTypeChecker):
    def __init__(self, name):
        DictTypeChecker.__init__(self, name, "")
        self.mAspectCheckers = []

    def regAspect(self, asp_h):
        asp_checker = None
        if asp_h.getColGroups() is None:
            if asp_h.getField() is not None:
                if asp_h.getMode() == "dict":
                    asp_checker = DictTypeChecker(
                        asp_h.getField(), self.getName(), base_asp = asp_h)
                    self.mAspectCheckers.append(asp_checker)
                elif asp_h.getMode() == "string":
                    attr_h = AttrH(asp_h.getField())
                    asp_checker = AttrTypeChecker(asp_h.getField(), attr_h)
                self.regIt(asp_checker)
            else:
                asp_checker = self
                assert self.mBaseAsp is None
                self.mBaseAsp = asp_h
        else:
            attr_names = asp_h.getColGroups().getAttrNames()
            if asp_h.getField() is not None:
                mid_checker = DictTypeChecker(
                    asp_h.getField(), self.getName(), base_asp = asp_h)
                asp_checker = ColGroupTypeChecker(
                    asp_h.getTitle(), mid_checker.getName(), None,
                    asp_h.getColGroups().hasSingleGroupCol())
                for nm in attr_names:
                    mid_checker.regIt(asp_checker, nm)
                self.regIt(mid_checker)
                self.mAspectCheckers.append(mid_checker)
            else:
                asp_checker = ColGroupTypeChecker(
                    asp_h.getTitle(), self.getName(), asp_h,
                    asp_h.getColGroups().hasSingleGroupCol())
                for nm in attr_names:
                    self.regIt(asp_checker, nm)
                self.mAspectCheckers.append(asp_checker)
        for attr_h in asp_h.getAttrs():
            asp_checker.addAttr(attr_h)

    def getKind(self):
        return "Source"

#===============================================
class ViewDataChecker(DictTypeChecker):
    def __init__(self, aspects):
        DictTypeChecker.__init__(self, "", "")
        self.mAspects = aspects
        self.mSources = []
        self.mProblems = defaultdict(list)
        for asp_h in self.mAspects:
            source_h = self.getReg(asp_h.getSource())
            if source_h is None:
                source_h = SourceTypeChecker(asp_h.getSource())
                self.regIt(source_h)
                self.mSources.append(source_h)
            source_h.regAspect(asp_h)

    def getKind(self):
        return "Top"

    def problem(self, code, checker, parent_checker = None):
        check_name = checker.getName()
        if parent_checker is not None:
            check_name = parent_checker.getName() + '.' + check_name
        self.mProblems[code].append(check_name)

    def finishUp(self, rep_output, no_mode = False):
        self.fixUp(self, rep_output, no_mode = no_mode)
        print("Data check result:", file = rep_output)
        group_name = None
        for code in sorted(self.mProblems.keys()):
            names = self.mProblems[code]
            print("\t", code, len(names), file = rep_output)
            for nm in names:
                grp, q, name = nm.partition('.')
                if grp != group_name:
                    print("\t\t", grp, file = rep_output)
                    group_name = grp
                if name is not None:
                    print("\t\t\t", name, file = rep_output)
        return "fatal" not in self.mProblems

#===============================================

import logging
from StringIO import StringIO

from .type_count import ValueTypeCounter
from .attr import AttrH

#===============================================
def techName(name):
    return name.startswith('_')

#===============================================
class BaseTypeChecker:
    def __init__(self, name):
        self.mName = name
        self.mReg = dict()

    def getName(self):
        return self.mName

    def _getReg(self, name):
        return self.mReg.get(name)

    def _addReg(self, reg, name = None):
        if name is None:
            name = reg.getName()
        assert name not in self.mReg
        self.mReg[name] = reg

    def _unexpectedReg(self, name):
        return ValueTypeCounter(name, state = "?")

    def _getRegNames(self):
        return sorted(self.mReg.keys())

    def _regItemVal(self, name, val):
        reg_h = self.mReg.get(name)
        if reg_h is None:
            reg_h = self._unexpectedReg(name)
            self._addReg(reg_h)
        reg_h.regValue(val)

#===============================================
class DictTypeChecker(BaseTypeChecker):
    def __init__(self, name, master_name, state = "ok", base_asp = None):
        BaseTypeChecker.__init__(self, name)
        self.mMasterName = master_name
        self.mBaseAsp = base_asp
        self.mAttrs = []
        self.mOwnCnt = ValueTypeCounter("=",
            required_type = "dict", state = state)

    def _getKind(self):
        return "Dict"

    def getBaseAsp(self):
        return self.mBaseAsp

    def _setBaseAsp(self, base_asp):
        self.mBaseAsp = base_asp

    def _addAttr(self, attr_h):
        if attr_h.getName() is None:
            return
        attr_tp_h = ValueTypeCounter(attr_h.getName(),
            attr_h.isSeq(), attr_h.getType())
        attr_h._setTpCnt(attr_tp_h)
        self._addReg(attr_tp_h)
        self.mAttrs.append(attr_h)

    def regValue(self, value):
        self.mOwnCnt.regValue(value)
        for name, val in value.items():
            self._regItemVal(name, val)

    def _getOwnCnt(self):
        return self.mOwnCnt

    def _getCheckers(self):
        return []

    def getUnexpectedRegs(self, keep_tech = True):
        all_names = set(self._getRegNames())
        for reg_h in self._getCheckers():
            all_names -= set(reg_h.getName().split('|'))
        for attr_h in self.mAttrs:
            nm = attr_h.getName()
            if nm in all_names:
                all_names.remove(nm)
        if not keep_tech:
            all_names = filter(lambda nm: not techName(nm), list(all_names))
        return sorted(all_names)

    def report(self, output, rep_level):
        if rep_level < 2 and techName(self.getName()):
            return
        for reg_h in self._getCheckers():
            reg_h.report(output, rep_level)
        print >> output, "==================="
        print >> output, self._getKind(), (
            self.mMasterName + '/' + self.getName())
        self.mOwnCnt.report(output, rep_level)
        for attr_h in self.mAttrs:
            if rep_level < 2 and attr_h.getName().startswith('_'):
                continue
            attr_h.getTpCnt().report(output, rep_level)
        for nm in self.getUnexpectedRegs():
            self._getReg(nm).report(output, rep_level)

    def fixUp(self, output, counts):
        for attr_h in self.mAttrs:
            rep = attr_h._checkTpCnt()
            if rep is not None:
                print >> output, (
                    "JSON-warn: Fix field format for %s: %s" % (
                        attr_h.getPath(), rep))
                counts[1] += 1

        bad_names = self.getUnexpectedRegs(False)
        if len(bad_names) == 0:
            return
        if self.mBaseAsp is None:
            print >> output, (
                "JSON-ERROR: Lost fields for %s/%s (%d): %s" % (
                self.mMasterName, self.getName(), len(bad_names),
                ", ".join(bad_names)))
            counts[0] += 1
        else:
            print >> output, (
                "JSON-warn: Fixing fields for %s/%s (%d): %s" % (
                self.mMasterName, self.getName(), len(bad_names),
                ", ".join(bad_names)))
            counts[1] +=1
            for nm in bad_names:
                self.mBaseAsp._addAttr(AttrH(nm, tp_cnt = self._getReg(nm)))

#===============================================
class TopTypeChecker(DictTypeChecker):
    def __init__(self):
        DictTypeChecker.__init__(self, "", "")
        self.mFrames = []

    def _getKind(self):
        return "Top"

    def _unexpectedReg(self, name):
        return FrameTypeChecker(name)

    def _getCheckers(self):
        return self.mFrames

    def regAspect(self, asp_h):
        if self._getReg(asp_h.getSource()) is None:
            frame_h = FrameTypeChecker(asp_h.getSource())
            self._addReg(frame_h)
            self.mFrames.append(frame_h)
        self._getReg(asp_h.getSource()).regAspect(asp_h)

    def fixUp(self, output, counts):
        for frame_h in self.mFrames:
            frame_h.fixUp(output, counts)
        DictTypeChecker.fixUp(self, output, counts)

#===============================================
class FrameTypeChecker(DictTypeChecker):
    def __init__(self, name):
        DictTypeChecker.__init__(self, name, "")
        self.mCheckers = []

    def _getKind(self):
        return "Frame"

    def _getCheckers(self):
        return self.mCheckers

    def regAspect(self, asp_h):
        colgrp_h = asp_h.getColGroups()
        if colgrp_h is None:
            if asp_h.getField() is not None:
                reg_h = DictTypeChecker(asp_h.getField(),
                    self.getName(), base_asp = asp_h)
                self._addReg(reg_h)
            else:
                reg_h = self
                if self.getBaseAsp() is None:
                    self._setBaseAsp(asp_h)
        else:
            attr_names = [colgrp_h.getAttr(idx)
                for idx in range(colgrp_h.getCount())]
            reg_h = ColGroupTypeChecker('|'.join(attr_names),
                self.getName(), asp_h)
            for nm in attr_names:
                self._addReg(reg_h, nm)
        if reg_h is not self:
            self.mCheckers.append(reg_h)
        for attr_h in asp_h.getAttrs():
            reg_h._addAttr(attr_h)
        asp_h._setTpCnt(self._getOwnCnt())

    def fixUp(self, output, counts):
        for frame_h in self.mCheckers:
            frame_h.fixUp(output, counts)
        DictTypeChecker.fixUp(self, output, counts)

#===============================================
class ColGroupTypeChecker(DictTypeChecker):
    def __init__(self, name, master_name, base_asp):
        DictTypeChecker.__init__(self, name, master_name, base_asp = base_asp)

    def _getKind(self):
        return "Columns"

    def regValue(self, value):
        for it in value:
            for name, val in it.items():
                self._regItemVal(name, val)

#===============================================
class ViewDataChecker:
    @classmethod
    def check(cls, view_setup, data_set, rep_level = 0):
        report = StringIO()
        top_reg = TopTypeChecker()
        good_attrs = set()
        for asp_h in view_setup.iterAspects():
            top_reg.regAspect(asp_h)
            asp_h._feedAttrPath(good_attrs)
        for obj in data_set.iterDataObjects():
            top_reg.regValue(obj)
        if rep_level > 0:
            top_reg.report(report, rep_level)
        err_counts = [0, 0]
        top_reg.fixUp(report, err_counts)
        if err_counts[0] > 0:
            print >> report, ("Errors in AJson %s" %
                data_set.getName())
        elif err_counts[1] > 0:
            print >> report, ("Warnings in AJson %s" %
                data_set.getName())
        else:
            print >> report, ("Attrs are all set for AJson %s"
                % data_set.getName())
        if err_counts[0] > 0:
            logging.error(report.getvalue())
        else:
            logging.warning(report.getvalue())

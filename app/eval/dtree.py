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

from app.config.a_config import AnfisaConfig
from .evaluation import Evaluation
from .dtree_parse import ParsedDTree
from .code_works import HtmlPresentation
#===============================================
class CaseStory:
    def __init__(self, parent = None, start = None):
        self.mParent = parent
        self.mPoints = []
        self.mStartPoint  = start

    def getMaster(self):
        if self.mParent is not None:
            return self.mParent.getMaster()
        assert False
        return None

    def getCurPointNo(self):
        if self.mParent is not None:
            return self.mParent.getCurPointNo()
        assert False
        return None

    def getLevel(self):
        if self.mParent is None:
            return 0
        return self.mParent.getLevel() + 1

    def _getStartPoint(self):
        return self.mStartPoint

    def _getLastPoint(self):
        if len(self.mPoints) > 0:
            return self.mPoints[-1]
        return self.mStartPoint

    def _addPoint(self, point):
        self.getMaster().regPoint(point)
        self.mPoints.append(point)

    def checkDetermined(self):
        if (len(self.mPoints) == 0
                or self.mPoints[-1].getPointKind() != "Return"):
            return self
        for cond_point in self.mPoints[:-1]:
            if not cond_point.isActive():
                continue
            ret = cond_point.getSubStory().checkDetermined()
            if ret is not None:
                return ret
        return None

#===============================================
class CheckPoint:
    def __init__(self, story, frag, prev_point):
        self.mStory = story
        self.mFrag = frag
        self.mPointNo = story.getCurPointNo()
        self.mPrevPoint = prev_point
        assert self.mFrag.getLevel() == self.mStory.getLevel()
        assert (self.mPrevPoint is None
            or self.mPrevPoint.getPointKind() == "If")

    def getStory(self):
        return self.mStory

    def getLevel(self):
        return self.mStory.getLevel()

    def getPrevPoint(self):
        return self.mPrevPoint

    def getPointKind(self):
        assert False

    def isActive(self):
        return True

    def getPointNo(self):
        return self.mPointNo

    def getDecision(self):
        return self.mFrag.getDecision()

    def getCondData(self):
        return self.mFrag.getCondData()

    def getMarkers(self):
        return self.mFrag.getMarkers()

    def _accumulateConditions(self):
        if self.getPrevPoint() is None:
            return self.mCondition
        assert self.getPrevPoint().getLevel() == self.getLevel()
        return self.getPrevPoint()._accumulateConditions().addOr(
            self.mCondition)

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getMaster().getEvalSpace().getCondAll()
        return self.getPrevPoint()._accumulateConditions().negative()

    def getInfo(self, code_lines):
        return [self.getPointKind(), self.getLevel(),
            self.getDecision(), self.getCondData(),
            self.getCodeFrag(code_lines)]

    def getCodeFrag(self, code_lines):
        line_from, line_to = self.mFrag.getLineDiap()
        return "\n".join(code_lines[line_from - 1: line_to - 1])

#===============================================
class LabelPoint(CheckPoint):
    def __init__(self, story, frag, prev_point):
        CheckPoint.__init__(self, story, frag, prev_point)

    def getPointKind(self):
        return "Label"

    def isActive(self):
        return False

#===============================================
class ErrorPoint(CheckPoint):
    def __init__(self, story, frag):
        CheckPoint.__init__(self, story, frag, None)

    def getPointKind(self):
        return "Error"

    def isActive(self):
        return False

#===============================================
class TerminalPoint(CheckPoint):
    def __init__(self, story, frag, prev_point):
        CheckPoint.__init__(self, story, frag, prev_point)

    def getPointKind(self):
        return "Return"

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getMaster().getEvalSpace().getCondAll()
        if self.getPrevPoint().getLevel() == self.getLevel():
            return self.getPrevPoint()._accumulateConditions().negative()
        return self.getPrevPoint().getAppliedCondition()

#===============================================
class ConditionPoint(CheckPoint):
    def __init__(self, story, frag, prev_point):
        CheckPoint.__init__(self, story, frag, prev_point)
        self.mCondition = self.getStory().getMaster().buildCondition(
            self.getCondData())
        self.mSubStory = CaseStory(self.getStory(), self)

    def getPointKind(self):
        return "If"

    def getSubStory(self):
        return self.mSubStory

    def getOwnCondition(self):
        return self.mCondition

    def getAppliedCondition(self):
        return self.actualCondition().addAnd(self.mCondition)

#===============================================
class DTreeEval(Evaluation, CaseStory):
    def __init__(self, eval_space, code, dtree_name = None,
            updated_time = None, updated_from = None):
        parsed = ParsedDTree(eval_space, code)
        Evaluation.__init__(self, eval_space, parsed.getHashCode(),
            updated_time, updated_from)
        CaseStory.__init__(self)
        self.mCode = parsed.getTreeCode()
        self.mDTreeName = dtree_name
        self.mPointList = None
        self.mFragments = parsed.getFragments()
        self.mFinalCondition = None

        self.mErrorInfo = None
        if parsed.getError() is not None:
            msg_text, lineno, offset = parsed.getError()
            self.mErrorInfo = {
                "line": lineno, "pos": offset, "error": msg_text}
            logging.error(("Error in tree %s code: (%d:%d) %s\n" %
                (dtree_name if dtree_name else "", lineno, offset, msg_text)))

    def isActive(self):
        return self.mPointList is not None

    def activate(self):
        if self.mPointList is not None:
            return
        self.mPointList = []
        prev_point = None
        for instr_no, frag_h in enumerate(self.mFragments):
            self.runNextPoint(instr_no, frag_h.getLabel())
            if frag_h.getInstrType() == "Label":
                assert frag_h.getDecision() is None
                self._addPoint(LabelPoint(self, frag_h, prev_point))
                continue
            if frag_h.getInstrType() == "Error":
                self._addPoint(ErrorPoint(self, frag_h))
                continue
            if frag_h.getInstrType() == "If":
                assert frag_h.getDecision() is None
                cond_point = ConditionPoint(self, frag_h, prev_point)
                self._addPoint(cond_point)
                prev_point = cond_point
                continue
            if frag_h.getInstrType() == "Return":
                assert frag_h.getCondData() is None
                if frag_h.getLevel() != 0:
                    assert frag_h.getLevel() == 1
                    prev_point.getSubStory()._addPoint(
                        TerminalPoint(prev_point.getSubStory(),
                            frag_h, prev_point))
                else:
                    self._addPoint(TerminalPoint(self, frag_h, prev_point))
                continue
            assert False, "Bad frag type: %s" % frag_h.getInstrType()
        self.finishRuntime()

    def operationError(self, cond_data, err_msg):
        Evaluation.operationError(self, cond_data, err_msg)
        for mark_info in self.mFragments[self.getCurPointNo()].getMarkers():
            if cond_data is mark_info.getCondData():
                mark_info.setError(err_msg)
                return
        assert False, "Marker not found: " + str(cond_data)

    def locateCondData(self, cond_data):
        for mark_info in self.mFragments[self.getCurPointNo()].getMarkers():
            if cond_data is mark_info.getCondData():
                return self.getCurPointNo(), mark_info.getErrorMsg()
        assert False, "Not found: " + str(cond_data)
        return None

    def __len__(self):
        return len(self.mPointList)

    def getSolKind(self):
        return "dtree"

    def getMaster(self):
        return self

    def getErrorInfo(self):
        return self.mErrorInfo

    def getCode(self):
        return self.mCode

    def getDTreeName(self):
        return self.mDTreeName

    def getCurPointNo(self):
        return Evaluation.getCurPointNo(self)

    def regPoint(self, point):
        assert point.getPointNo() == len(self.mPointList)
        self.mPointList.append(point)

    def pointNotActive(self, point_no):
        return not self.mPointList[point_no].isActive()

    def getActualCondition(self, point_no):
        return self.mPointList[point_no].actualCondition()

    def checkZeroAfter(self, point_no):
        return self.mPointList[point_no].getPointKind() == "If"

    def reportInfo(self):
        marker_seq = []
        marker_dict = {}
        for point in self.mPointList:
            cond_seq = []
            for mark_idx, mark_info in enumerate(point.getMarkers()):
                marker_seq.append((point.getPointNo(), mark_idx,
                    mark_info.getLoc(), mark_info.getErrorMsg()))
                cond_seq.append(mark_info.getCondData())
            if len(cond_seq) > 0:
                marker_dict[point.getPointNo()] = cond_seq
        html_lines = self._decorCode(marker_seq)
        ret_handle = {
            "points": [point.getInfo(html_lines) for point in self.mPointList],
            "markers": marker_dict,
            "labels": self.getLabelPoints(),
            "code": self.mCode,
            "hash": self.mHashCode,
            "eval-status": self.getEvalStatus()}
        if self.mErrorInfo:
            ret_handle.update(self.mErrorInfo)
        if self.mDTreeName:
            ret_handle["dtree-name"] = self.mDTreeName
        return ret_handle

    def _decorCode(self, marker_seq = None):
        code_lines = self.mCode.splitlines()
        html_lines = []
        cur_diap = None

        for frag_h in self.mFragments:
            if frag_h.getInstrType() == "Error":
                if cur_diap is not None:
                    html_lines += HtmlPresentation.decorProperCode(
                        code_lines, cur_diap, marker_seq)
                    cur_diap = None
                html_lines += HtmlPresentation.presentErrorCode(
                    code_lines, frag_h.getLineDiap(), frag_h.getErrorInfo())
            else:
                if cur_diap is None:
                    cur_diap = frag_h.getLineDiap()
                else:
                    cur_diap = [cur_diap[0], frag_h.getLineDiap()[1]]
        if cur_diap is not None:
            html_lines += HtmlPresentation.decorProperCode(
                code_lines, cur_diap, marker_seq)
        return html_lines

    def collectRecSeq(self):
        max_ws_size = AnfisaConfig.configOption("max.ws.size")
        html_lines = self._decorCode()
        ret = set()
        info_seq = []
        for point in self.mPointList:
            info_seq.append([point.getCodeFrag(html_lines), None, None])
            if not point.isActive():
                continue
            condition = point.actualCondition()
            point_count = self.getEvalSpace().evalTotalCount(condition)
            info_seq[-1][1] = point_count
            if point.getPointKind() == "Return":
                info_seq[-1][2] = point.getDecision()
            if point.getDecision() is True:
                assert point.getPointKind() == "Return"
                assert point_count < max_ws_size
                if point_count > 0:
                    seq = self.getEvalSpace().evalRecSeq(
                        condition, point_count)
                    ret |= set(seq)
            assert len(ret) < max_ws_size
        return sorted(ret), info_seq

    def getFinalCondition(self):
        assert self.getEvalSpace().getCondKind() == "ws"
        if self.mFinalCondition is None:
            cond_seq = []
            for point in self.mPointList:
                if point.isActive() and point.getDecision() is True:
                    cond_seq.append(point.actualCondition())
            self.mFinalCondition = self.getEvalSpace().joinOr(cond_seq)
        return self.mFinalCondition

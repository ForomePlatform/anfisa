import logging
from app.config.a_config import AnfisaConfig
from .code_works import htmlCodeDecoration
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

    def getCondEnv(self):
        return self.getMaster().getCondEnv()

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
        assert (len(self.mPoints) == 0 or
            self.mPoints[-1].getPointKind() == "If")
        self.getMaster().regPoint(point)
        self.mPoints.append(point)

    def checkDetermined(self):
        if (len(self.mPoints) == 0 or
                self.mPoints[-1].getPointKind() != "Return"):
            return self
        for cond_point in self.mPoints[:-1]:
            ret = cond_point.getSubStory().checkDetermined()
            if ret is not None:
                return ret
        return None

#===============================================
class CheckPoint:
    def __init__(self, story, frag, prev_point, point_no):
        self.mStory = story
        self.mFrag = frag
        self.mPointNo = point_no
        self.mPrevPoint = prev_point
        assert self.mFrag.getLevel() == self.mStory.getLevel()
        assert (self.mPrevPoint is None or
            self.mPrevPoint.getPointKind() == "If")

    def getStory(self):
        return self.mStory

    def getLevel(self):
        return self.mStory.getLevel()

    def getPrevPoint(self):
        return self.mPrevPoint

    def getPointKind(self):
        assert False

    def getPointNo(self):
        return self.mPointNo

    def getDecision(self):
        return self.mFrag.getDecision()

    def getCondData(self):
        return self.mFrag.getCondData()

    def getMarkers(self):
        return self.mFrag.getMarkers()

    def getInfo(self, code_lines):
        line_from, line_to = self.mFrag.getFullLineDiap()
        return [self.getPointKind(), self.getLevel(),
            self.getDecision(), self.getCondData(),
            "\n".join(code_lines[line_from - 1: line_to])]

#===============================================
class TerminalPoint(CheckPoint):
    def __init__(self, story, frag, prev_point, point_no):
        CheckPoint.__init__(self, story, frag, prev_point, point_no)

    def getPointKind(self):
        return "Return"

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getCondEnv().getCondAll()
        if self.getPrevPoint().getLevel() == self.getLevel():
            return self.getPrevPoint()._accumulateConditions().negative()
        return self.getPrevPoint().getAppliedCondition()

#===============================================
class ConditionPoint(CheckPoint):
    def __init__(self, story, frag, prev_point, point_no):
        CheckPoint.__init__(self, story, frag, prev_point, point_no)
        self.mCondition = self.getStory().getMaster().getCondEnv().parse(
            self.getCondData())
        self.mSubStory = CaseStory(self.getStory(), self)

    def getPointKind(self):
        return "If"

    def getSubStory(self):
        return self.mSubStory

    def getOwnCondition(self):
        return self.mCondition

    def _accumulateConditions(self):
        if self.getPrevPoint() is None:
            return self.mCondition
        assert self.getPrevPoint().getLevel() == self.getLevel()
        return self.getPrevPoint()._accumulateConditions().addOr(
            self.mCondition)

    def actualCondition(self):
        if self.getPrevPoint() is None:
            return self.getStory().getCondEnv().getCondAll()
        return self.getPrevPoint()._accumulateConditions().negative()

    def getAppliedCondition(self):
        return self.actualCondition().addAnd(self.mCondition)

#===============================================
class DecisionTree(CaseStory):
    def __init__(self, parsed):
        CaseStory.__init__(self)
        if parsed.getError() is not None:
            msg_text, lineno, offset = parsed.getError()
            logging.error(("Error in tree code: (%d:%d) %s\n" %
                (lineno, offset, msg_text)) + "Code:\n======\n" +
                parsed.getTreeCode() + "\n======")
            assert False
        self.mCondEnv = parsed.getCondEnv()
        self.mCode = parsed.getTreeCode()
        self.mPointList = []
        prev_point = None
        for instr_no, frag in enumerate(parsed.getFragments()):
            if frag.getInstrType() == "If":
                assert frag.getDecision() is None
                cond_point = ConditionPoint(self, frag, prev_point, instr_no)
                self._addPoint(cond_point)
                prev_point = cond_point
                continue
            elif frag.getInstrType() == "Return":
                assert frag.getCondData() is None
                if frag.getLevel() != 0:
                    assert frag.getLevel() == 1
                    prev_point.getSubStory()._addPoint(TerminalPoint(
                        prev_point.getSubStory(), frag, prev_point, instr_no))
                else:
                    self._addPoint(TerminalPoint(self,
                        frag, prev_point, instr_no))
            else:
                assert False
        assert self.checkDetermined() is None

    def __len__(self):
        return len(self.mPointList)

    def getMaster(self):
        return self

    def getCondEnv(self):
        return self.mCondEnv

    def regPoint(self, point):
        assert point.getPointNo() == len(self.mPointList)
        self.mPointList.append(point)

    def actualCondition(self, point_no):
        return self.mPointList[point_no].actualCondition()

    def dump(self):
        marker_seq = []
        marker_dict = {}
        for point in self.mPointList:
            cond_seq = []
            for mark_idx, mark_info in enumerate(point.getMarkers()):
                point_cond, name_instr = mark_info
                marker_seq.append((point.getPointNo(), mark_idx, name_instr))
                cond_seq.append(point_cond)
            if len(cond_seq) > 0:
                marker_dict[point.getPointNo()] = cond_seq
        html_lines = htmlCodeDecoration(self.mCode, marker_seq)
        return {
            "points": [point.getInfo(html_lines) for point in self.mPointList],
            "markers": marker_dict,
            "code": self.mCode}

    def collectRecSeq(self, dataset):
        max_ws_size = AnfisaConfig.configOption("max.ws.size")
        ret = set()
        for point in self.mPointList:
            if point.getDecision() is True:
                assert point.getPointKind() == "Return"
                condition = point.actualCondition()
                point_count = dataset.evalTotalCount(condition)
                assert point_count < max_ws_size
                if point_count > 0:
                    seq = dataset.evalRecSeq(condition, point_count)
                    ret |= set(seq)
            assert len(ret) < max_ws_size
        return sorted(ret)

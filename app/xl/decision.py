from collections import defaultdict

from xl_cond import XL_Condition, XL_None
#===============================================
class PointCounter:
    def __init__(self, count = None):
        self.mCount = count

    def getCount(self):
        return self.mCount

    def setCount(self, count):
        self.mCount = count

#===============================================
class CaseStory:
    def __init__(self, parent = None, start = None):
        self.mParent = parent
        self.mPoints = []
        self.mStart  = start

    def getMaster(self):
        if self.mParent is not None:
            return self.mParent.getMaster()
        return self

    def getLevel(self):
        if self.mParent is None:
            return 0
        return self.mParent.getLevel() + 1

    def getStart(self):
        return self.mStart

    def addComment(self, comment):
        self.mParent.addComment(comment)

    def __addPoint(self, point):
        assert (len(self.mPoints) == 0 or
            self.mPoints[-1].getPointKind() == "cond")
        self.getMaster().regPoint(point)
        self.mPoints.append(point)

    def addCondition(self, condition, decision = None, count = None):
        prev_point  = (self.mStart if len(self.mPoints) == 0 else
            self.mPoints[-1])
        cond_point = ConditionPoint(self, prev_point,
            self.getMaster().nextNo(), condition, count)
        self.__addPoint(cond_point)
        if decision is not None:
            cond_point.getSubStory().setFinalDecision(decision)
        return cond_point

    def setFinalDecision(self, decision, count = None):
        prev_point  = (self.mStart if len(self.mPoints) == 0 else
            self.mPoints[-1])
        self.__addPoint(TerminalPoint(self, prev_point,
            self.getMaster().nextNo(), decision, count))

    def checkDetermined(self):
        if (len(self.mPoints) == 0 or
                self.mPoints[-1].getPointKind() != "term"):
            return self
        for cond_point in self.mPoints[:-1]:
            ret = cond_point.getSubStory().checkDetermined()
            if ret is not None:
                return ret
        return None

    def dump(self):
        ret = ["story"]
        for point in self.mPoints:
            ret.append(point.dump())
        return ret

#===============================================
class CheckPoint(PointCounter):
    def __init__(self, story, prev_point, point_no, count = None):
        PointCounter.__init__(self, count)
        self.mStory = story
        self.mPointNo = point_no
        self.mPrevPoint = prev_point
        assert (self.mPrevPoint is None or
            self.mPrevPoint.getPointKind() == "cond")

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

    def dump(self):
        return [self.getPointKind(), self.mPointNo,
            self.getLevel(), self.mCount]

#===============================================
class TerminalPoint(CheckPoint):
    def __init__(self, story, prev_point, point_no, decision, count = None):
        CheckPoint.__init__(self, story, prev_point, point_no, count)
        self.mDecision = decision

    def getPointKind(self):
        return "term"

    def getDecision(self):
        return self.mDecision

    def actualCondition(self):
        if self.mPrevPoint is None:
            return XL_None()
        return self.getPrevPoint().getWorkCondition()

    def dump(self):
        return CheckPoint.dump(self) + [self.mDecision]

#===============================================
class ConditionPoint(CheckPoint):
    def __init__(self, story, prev_point, point_no, condition, count = None):
        CheckPoint.__init__(self, story, prev_point, point_no, count)
        self.mColdCondition = condition
        self.mCondition = XL_Condition.parse(self.mColdCondition)
        self.mSubStory = CaseStory(self.getStory(), self)

    def getPointKind(self):
        return "cond"

    def getSubStory(self):
        return self.mSubStory

    def getOwnCondition(self):
        return self.mCondition

    def accumulateConditions(self):
        if self.getPrevPoint() is None:
            return self.mCondition
        # TRF: extend it
        assert self.getPrevPoint().getLevel() == self.getLevel()
        return self.getPrevPoint().accumulateConditions().addOr(
            self.mCondition)

    def actualCondition(self):
        if self.mPrevPoint is None:
            return XL_None()
        return self.mPrevPoint.accumulateConditions().negative()

    def getWorkCondition(self):
        if self.mPrevPoint is None:
            return self.mCondition
        return self.mCondition.addAnd(
            self.mPrevPoint.accumulateConditions().negative())

    def dump(self):
        return CheckPoint.dump(self) + [self.mColdCondition]

#===============================================
class DecisionTree(CaseStory):
    def __init__(self, stat = None):
        CaseStory.__init__(self, start = None)
        self.mComments = defaultdict(list)
        self.mPointList = []
        self.mStat = stat

    def nextNo(self):
        return len(self.mPointList)

    def regPoint(self, point):
        assert point.getPointNo() == len(self.mPointList)
        self.mPointList.append(point)

    def addComment(self, comment):
        self.mComments[len(self.mPointList)].append(comment)

    def actualCondition(self, point_no):
        return self.mPointList[point_no].actualCondition()

    def dump(self):
        ret = [["tree", self.mStat]]
        for point_no, point in enumerate(self.mPointList):
            comments = self.mComments.get(point_no)
            if comments:
                for comment in comments:
                    ret.append(["comment", comment])
            ret.append(point.dump())
        return ret

    @staticmethod
    def parse(json_data):
        assert json_data[0][0] == "tree"
        ret = DecisionTree(json_data[1])
        stories = [ret]
        for rec in json_data[1:]:
            if rec[0] == "comment":
                ret.addComment(rec[1])
                continue
            p_kind, p_no, p_level, p_count = rec[:4]
            assert p_level == len(stories) - 1
            if rec[0] == "cond":
                point = stories[-1].addCondition(rec[4], count = p_count)
                stories.append(point.getSubStory())
            else:
                assert rec[0] == "term"
                stories[-1].setFinalDecision(rec[4], count = p_count)
                stories.pop()
        assert ret.checkDetermined() is None
        return ret

    def evalCounts(self, dataset):
        counts = [dataset.evalTotalCount(None)]
        self.mStat = [counts[0], 0, 0]
        for point in self.mPointList:
            point.setCount(counts[-1])
            if point.getPointKind() == "cond":
                #print >> sys.stderr, point.getPointNo(), "RQ:", json.dumps(
                #    point.getWorkCondition().getDruidRepr(), indent = 4)
                if counts[-1] > 0:
                    flt_count = dataset.evalTotalCount(
                        point.getWorkCondition())
                else:
                    flt_count = 0
                #print >> sys.stderr, "Cnt:", flt_count, counts
                assert flt_count <= counts[-1]
                counts[-1] -= flt_count
                counts.append(flt_count)
            else:
                assert point.getPointKind() == "term"
                rest_count = counts.pop()
                if point.getDecision() is True:
                    self.mStat[1] += rest_count
                elif point.getDecision() is False:
                    self.mStat[2] += rest_count
        assert len(counts) == 0

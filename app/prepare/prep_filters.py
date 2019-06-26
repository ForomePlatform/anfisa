import app.prepare.prep_unit as prep_unit
from app.model.family import FamilyInfo
from app.filter.cond_env import CondEnv
#===============================================
class FilterPrepareSetH:
    def __init__(self, modes = None):
        self.mUnits = []
        self.mVGroups  = dict()
        self.mCurVGroup = None
        self.mMeta = None
        self.mFamilyInfo = None
        self.mCondEnv = CondEnv(modes)

    def setMeta(self, meta):
        self.mMeta = meta
        self.mFamilyInfo = FamilyInfo.detect(self.mMeta["samples"])

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
            default_value = None, diap = None,
            render_mode = None, tooltip = None, research_only = False):
        return self._addUnit(prep_unit.IntConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            research_only, default_value, diap))

    def floatValueUnit(self, name, path, title = None,
            default_value = None, diap = None,
            render_mode = None, tooltip = None, research_only = False):
        return self._addUnit(prep_unit.FloatConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            research_only, default_value, diap))

    def statusUnit(self, name, path, title = None,
            variants = None, default_value = "False",
            accept_other_values = False,
            render_mode = None, tooltip = None, research_only = False):
        return self._addUnit(prep_unit.EnumConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            research_only, True, variants, default_value,
            accept_other_values = accept_other_values))

    def presenceUnit(self, name, var_info_seq, title = None,
            render_mode = None, tooltip = None, research_only = False):
        return self._addUnit(prep_unit.PresenceConvertor(name, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            research_only, var_info_seq))

    def multiStatusUnit(self, name, path, title = None,
            variants = None, default_value = None,
            separators = None, compact_mode = False,
            accept_other_values = False,
            render_mode = None, tooltip = None, research_only = False):
        return self._addUnit(prep_unit.EnumConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup, render_mode, tooltip,
            research_only, False, variants, default_value,
            separators = separators, compact_mode = compact_mode,
            accept_other_values = accept_other_values))

    def zygositySpecialUnit(self, name, path, title = None,
            default_value = None, config = None,
            render_mode = None, tooltip = None, research_only = False,):
        return self._addUnit(prep_unit.ZygosityConvertor(name, path, title,
            len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip, research_only, config, self))

    def panelStatusUnit(self, name, unit_base, title = None,
            render_mode = None, tooltip = None,
            research_only = False, view_path = None):
        return self._addUnit(prep_unit.PanelConvertor(self.mCondEnv,
            name, title, len(self.mUnits), self.mCurVGroup,
            render_mode, tooltip, research_only, unit_base, view_path))

    def process(self, rec_no, rec_data):
        result = dict()
        for unit in self.mUnits:
            unit.process(rec_no, rec_data, result)
        return result

    def reportProblems(self, output):
        for unit in self.mUnits:
            if unit.getErrorCount() > 0:
                print >> output, "Field %s: %d bad conversions" % (
                    unit.getName(), unit.getErrorCount())
        return True

    def dump(self):
        return [unit.dump() for unit in self.mUnits]

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

    def __exit__(self, type, value, traceback):
        self.mFilterSet._endViewGroup(self)

    def addUnit(self, unit):
        self.mUnits.append(unit)

    def getTitle(self):
        return self.mTitle

    def getUnits(self):
        return self.mUnits

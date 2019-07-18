import logging

from .sol_pack import SolutionPack
#===============================================
class CondEnv:
    def __init__(self, modes):
        self.mSolPack = SolutionPack.select(modes)
        self.mSpecialUnits = dict()
        self.mNumUnits = dict()
        self.mEnumUnits = dict()
        self.mOperativeUnits = dict()
        self.mReservedNames = dict()
        self.mOpUnitSeq = []
        self.mModes = set(modes) if modes else set()

    def addMode(self, mode):
        self.mModes.add(mode)

    def addNumUnit(self, unit_h):
        assert unit_h.getName() not in self.mNumUnits
        self.mNumUnits[unit_h.getName()] = unit_h

    def addEnumUnit(self, unit_h):
        assert unit_h.getName() not in self.mEnumUnits
        self.mEnumUnits[unit_h.getName()] = unit_h

    def addSpecialUnit(self, unit_h):
        assert unit_h.getName() not in self.mSpecialUnits
        self.mSpecialUnits[unit_h.getName()] = unit_h

    def addOperativeUnit(self, unit_h):
        assert unit_h.getName() not in self.mOperativeUnits
        self.mOperativeUnits[unit_h.getName()] = unit_h
        self.mOpUnitSeq.append(unit_h)

    def addReservedName(self, unit_name, rec_func = None):
        if unit_name not in self.mReservedNames:
            self.mReservedNames[unit_name] = _ReservedUnit(
                unit_name, rec_func)

    def iterOpUnits(self):
        return iter(self.mOpUnitSeq)

    def nameIsReserved(self, name):
        return name in self.mReservedNames

    def detectUnit(self, unit_name,
            expect_kind = None, use_logging = True):
        unit_kind, unit_h = self._detectUnit(unit_name)
        if expect_kind == "panel" and unit_kind == "enum":
            return "panel", unit_h
        if (use_logging and expect_kind is not None and
                expect_kind != unit_kind and
                unit_kind not in {"special","reserved", "operational"}):
            logging.warning("Mix-up in unit kinds for name=%s/%s asked %s" %
                (unit_name, unit_kind, str(expect_kind)))
            return None, None
        return unit_kind, unit_h

    def _detectUnit(self, unit_name):
        if unit_name in self.mOperativeUnits:
            return ("operational", self.mOperativeUnits[unit_name])
        if unit_name in self.mNumUnits:
            return ("numeric", self.mNumUnits[unit_name])
        if unit_name in self.mEnumUnits:
            return ("enum", self.mEnumUnits[unit_name])
        if unit_name in self.mSpecialUnits:
            return ("special", self.mSpecialUnits[unit_name])
        if unit_name in self.mReservedNames:
            return ("reserved", self.mReservedNames[unit_name])
        return None, None

    def joinAnd(self, seq):
        ret = self.getCondAll()
        for cond in seq:
            ret = ret.addAnd(cond)
        return ret

    def joinOr(self, seq):
        ret = self.getCondNone()
        for cond in seq:
            ret = ret.addOr(cond)
        return ret

    def parse(self, cond_info, op_data = None):
        if len(cond_info) == 0:
            return self.getCondAll()
        if cond_info[0] is None:
            assert len(cond_info) == 1
            return self.getCondNone()
        if cond_info[0] == "and":
            return self.joinAnd(
                [self.parse(cc, op_data) for cc in cond_info[1:]])
        if cond_info[0] == "or":
            return self.joinOr(
                [self.parse(cc, op_data) for cc in cond_info[1:]])
        if cond_info[0] == "not":
            assert len(cond_info) == 2
            return self.parse(cond_info[1], op_data).negative()

        pre_unit_kind, unit_name = cond_info[:2]
        unit_kind, unit_h = self.detectUnit(unit_name, pre_unit_kind)
        if unit_kind == "operational":
            return unit_h.parseCondition(cond_info, op_data[unit_name])
        if unit_kind == "reserved":
            unit_kind = cond_info[0]
        if unit_kind == "special":
            return unit_h.parseCondition(cond_info)
        if cond_info[0] == "numeric":
            bounds, use_undef = cond_info[2:]
            return self.makeNumericCond(unit_h, bounds, use_undef)
        if unit_kind == "panel":
            filter_mode, panel_name = cond_info[2:]
            variants = self.getUnitPanel(unit_name, panel_name)
            return self.makeEnumCond(unit_h, filter_mode, variants)
        if cond_info[0] == "enum":
            filter_mode, variants = cond_info[2:]
            return self.makeEnumCond(unit_h, filter_mode, variants)
        assert False
        return self.getCondNone()


    #===============================================
    def testRequirements(self, modes):
        if not modes:
            return True
        return len(modes & self.mModes) == len(modes)

    def reportSolutions(self):
        return {
            "codes": [it.getName() for it in self.mSolPack.iterItems(
                "tree_code", self.testRequirements)],
            "panels": [it.getName() for it in self.mSolPack.iterItems(
                "panel", self.testRequirements)]}
        pass

    def getWsFilters(self):
        return [(it.getName(), it.getData())
            for it in self.mSolPack.iterItems("flt_ws", self.testRequirements)]

    def getXlFilters(self):
        return [(it.getName(), it.getData())
            for it in self.mSolPack.iterItems("flt_xl", self.testRequirements)]

    def getUnitPanelNames(self, unit_name):
        ret = []
        for it in self.mSolPack.iterItems("panel", self.testRequirements):
            if it.getName() == unit_name:
                ret.append(it.getData()[0])
        return ret

    def getUnitPanel(self, unit_name, panel_name):
        for it in self.mSolPack.iterItems("panel", self.testRequirements):
            if it.getName() == unit_name:
                if it.getData()[0] == panel_name:
                    return it.getData()[1]
        assert False, "{} Panel {} not found".format(unit_name, panel_name)

    def getStdTreeCodeNames(self):
        return [it.getName() for it in
            self.mSolPack.iterItems("tree_code", self.testRequirements)]

    def getStdTreeCode(self, code_name):
        for it in self.mSolPack.iterItems("tree_code", self.testRequirements):
            if it.getName() == code_name or code_name is None:
                return it.getData()
        logging.error("Request for bad std tree: " + code_name)
        assert False

    def getStdTreeNameByHash(self, hash_code):
        it = self.mSolPack.getTreeByHashCode(hash_code)
        if it and it.testIt("tree_code", self.testRequirements):
            return it.getName()
        return None

#===============================================
class _ReservedUnit:
    def __init__(self, name, rec_func = None):
        self.mName = name
        self.mRecFunc = rec_func

    def getName(self):
        return self.mName

    def getRecFunc(self):
        return self.mRecFunc

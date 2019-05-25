import logging
#===============================================
class CondEnv:
    def __init__(self):
        self.mSpecialUnits = dict()
        self.mNumUnits = dict()
        self.mEnumUnits = dict()
        self.mOperativeUnits = dict()
        self.mReservedNames = set()

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

    def addReservedName(self, unit_name):
        self.mReservedNames.add(unit_name)

    def detectUnit(self, unit_name,
            expect_kind = None, use_logging = True):
        unit_kind, unit_h = self._detectUnit(unit_name)
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
            return ("reserved", None)
        return None, None

from app.filter.cond_env import CondEnv

#===============================================
class WS_CondEnv(CondEnv):
    def __init__(self, modes):
        CondEnv.__init__(self, modes)

    def getCondNone(self):
        return WS_None()

    def getCondAll(self):
        return WS_All()

    def makeNumericCond(self, unit_h, bounds, use_undef):
        return WS_NumCondition(unit_h.getName(), bounds, use_undef,
                unit_h.getRecFunc())

    def makeEnumCond(self, unit_h, filter_mode, variants):
        return WS_EnumCondition(unit_h.getName(), filter_mode, variants,
            unit_h.getVariantSet(), unit_h.getRecFunc())


#===============================================
class WS_Condition:
    def __init__(self):
        pass

    def __not__(self):
        assert False

    def __and__(self, other):
        assert False

    def __or__(self, other):
        assert False

    def addOr(self, other):
        assert other is not None and other.getCondKind() is not None
        if other.getCondKind() == "or":
            return other.addOr(self)
        elif other.getCondKind() == "null":
            return self
        return WS_Or([self, other])

    def addAnd(self, other):
        assert other is not None and other.getCondKind() is not None
        if other.getCondKind() == "and":
            return other.addAnd(self)
        elif other.getCondKind() == "null":
            return self
        return WS_And([self, other])

    def negative(self):
        return WS_Negation(self)

    def getCondKind(self):
        assert False

    def __call__(self, record):
        assert False

    def getCondNone(self):
        return WS_None()

    def getCondAll(self):
        return WS_All()

#===============================================
class WS_NumCondition(WS_Condition):
    def __init__(self, unit_name, bounds, use_undef, num_func):
        WS_Condition.__init__(self)
        self.mUnitName = unit_name
        self.mEvalFunc = self.numericFilterFunc(
            bounds[0], bounds[1], use_undef)
        self.mBounds = bounds
        self.mRecNumFunc = num_func

    def getCondKind(self):
        return "num"

    def __call__(self, record):
        return self.mEvalFunc(self.mRecNumFunc(record))

    @staticmethod
    def numericFilterFunc(bound_min, bound_max, use_undef):
        if bound_min is None:
            if bound_max is None:
                if use_undef:
                    return lambda val: val is None
                assert False
                return lambda val: True
            if use_undef:
                return lambda val: val is None or val <= bound_max
            return lambda val: val is not None and val <= bound_max
        if bound_max is None:
            if use_undef:
                return lambda val: val is None or bound_min <= val
            return lambda val: val is not None and bound_min <= val
        if use_undef:
            return lambda val: val is None or (
                bound_min <= val <= bound_max)
        return lambda val: val is not None and (
            bound_min <= val <= bound_max)

#===============================================
class WS_EnumCondition(WS_Condition):
    def __init__(self, unit_name, filter_mode, variants,
            variant_set, enum_func):
        WS_Condition.__init__(self)
        self.mUnitName = unit_name
        self.mEvalFunc = self.enumFilterFunc(filter_mode,
            variant_set.makeIdxSet(variants))
        self.mRecEnumFunc = enum_func

    def getCondKind(self):
        return "enum"

    def __call__(self, record):
        return self.mEvalFunc(self.mRecEnumFunc(record))

    @staticmethod
    def enumFilterFunc(filter_mode, base_idx_set):
        if filter_mode == "NOT":
            return lambda idx_set: len(idx_set & base_idx_set) == 0
        if filter_mode == "ONLY":
            return lambda idx_set: (len(idx_set) > 0 and
                len(idx_set - base_idx_set) == 0)
        if filter_mode == "AND":
            all_len = len(base_idx_set)
            return lambda idx_set: len(idx_set & base_idx_set) == all_len
        return lambda idx_set: len(idx_set & base_idx_set) > 0

#===============================================
class WS_SpecCondition(WS_Condition):
    def __init__(self, sub_kind, spec_func):
        WS_Condition.__init__(self)
        self.mKind = "spec/" + sub_kind
        self.mSpecFunc = spec_func

    def getCondKind(self):
        return self.mKind

    def __call__(self, record):
        return self.mSpecFunc(record)

#===============================================
class WS_Negation(WS_Condition):
    def __init__(self, base_cond):
        WS_Condition.__init__(self)
        self.mBaseCond = base_cond

    def negative(self):
        return self.mBaseCond

    def getCondKind(self):
        return "neg"

    def __call__(self, record):
        return not self.mBaseCond(record)

#===============================================
class _WS_Joiner(WS_Condition):
    def __init__(self, items):
        WS_Condition.__init__(self)
        self.mItems = items
        assert len(self.mItems) > 0

    def getItems(self):
        return self.mItems


#===============================================
class WS_And(_WS_Joiner):
    def __init__(self, items):
        _WS_Joiner.__init__(self, items)

    def getCondKind(self):
        return "and"

    def addAnd(self, other):
        if other.getCondKind() == "and":
            add_items = other.getItems()
        else:
            add_items = [other]
        return WS_And(self.getItems() + add_items)

    def __call__(self, record):
        for it in self.getItems():
            if not it(record):
                return False
        return True

#===============================================
class WS_Or(_WS_Joiner):
    def __init__(self, items):
        _WS_Joiner.__init__(self, items)

    def getCondKind(self):
        return "or"

    def addOr(self, other):
        if other.getCondKind() == "or":
            add_items = other.getItems()
        else:
            add_items = [other]
        return WS_Or(self.getItems() + add_items)

    def __call__(self, record):
        for it in self.getItems():
            if it(record):
                return True
        return False

#===============================================
class WS_None(WS_Condition):
    def __init__(self):
        WS_Condition.__init__(self)

    def addAnd(self, other):
        return self

    def addOr(self, other):
        return other

    def negative(self):
        return WS_All()

    def getCondKind(self):
        return "null"

    def __call__(self, record):
        return False

#===============================================
class WS_All(WS_Condition):
    def __init__(self):
        WS_Condition.__init__(self)

    def addAnd(self, other):
        return other

    def addOr(self, other):
        return self

    def negative(self):
        return WS_None()

    def getCondKind(self):
        return "all"

    def __call__(self, record):
        return True

#===============================================

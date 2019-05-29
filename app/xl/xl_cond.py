from app.filter.cond_env import CondEnv
#===============================================
class XL_CondEnv(CondEnv):
    def __init__(self):
        CondEnv.__init__(self)

    def getCondNone(self):
        return XL_None()

    def getCondAll(self):
        return XL_All()

    def makeNumericCond(self, unit_h, bounds, use_undef):
        return XL_NumCondition(unit_h.getName(), bounds, use_undef)

    def makeEnumCond(self, unit_h, filter_mode, variants):
        if len(variants) == 0:
            return XL_All() if filter_mode == "NOT" else XL_None()
        if filter_mode == "AND":
            return self.joinAnd([XL_EnumSingleCondition(
                unit_h.getName(), variant) for variant in variants])
        if len(variants) == 1:
            cond = XL_EnumSingleCondition(unit_h.getName(), variants[0])
        else:
            cond = XL_EnumInCondition(unit_h.getName(), variants)
        if filter_mode == "NOT":
            return XL_Negation(cond)
        return cond

#===============================================
class XL_Condition:
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
        return XL_Or([self, other])

    def addAnd(self, other):
        assert other is not None and other.getCondKind() is not None
        if other.getCondKind() == "and":
            return other.addAnd(self)
        elif other.getCondKind() == "null":
            return self
        return XL_And([self, other])

    def negative(self):
        return XL_Negation(self)

    def getCondKind(self):
        assert False

    def getDruidRepr(self):
        assert False

#===============================================
class XL_NumCondition(XL_Condition):
    def __init__(self, unit_name, bounds, use_undef = False):
        XL_Condition.__init__(self)
        self.mUnitName = unit_name
        self.mBounds = bounds
        self.mUseUndef = use_undef

    def getCondKind(self):
        return "num"

    def getDruidRepr(self):
        # use_undef ignored
        ret = {
            "type": "bound",
            "dimension": self.mUnitName,
            "lowerStrict": False,
            "upperStrict": False,
            "ordering": "numeric" }
        if self.mBounds[0] is not None:
            ret["lower"] = str(self.mBounds[0])
        if self.mBounds[1] is not None:
            ret["upper"] = str(self.mBounds[1])
        return ret

#===============================================
class XL_EnumSingleCondition(XL_Condition):
    def __init__(self, unit_name, variant):
        XL_Condition.__init__(self)
        self.mUnitName = unit_name
        self.mVariant = variant

    def getCondKind(self):
        return "enum-single"

    def getDruidRepr(self):
        return {
            "type": "selector",
            "dimension": self.mUnitName,
            "value": self.mVariant }

#===============================================
class XL_EnumInCondition(XL_Condition):
    def __init__(self, unit_name, variants):
        XL_Condition.__init__(self)
        self.mUnitName = unit_name
        self.mVariants = sorted(variants)

    def getCondKind(self):
        return "enum-in"

    def getDruidRepr(self):
        return {
            "type": "in",
            "dimension": self.mUnitName,
            "values": self.mVariants }

#===============================================
class XL_Negation(XL_Condition):
    def __init__(self, base_cond):
        XL_Condition.__init__(self)
        self.mBaseCond = base_cond

    def negative(self):
        return self.mBaseCond

    def getCondKind(self):
        return "neg"

    def getDruidRepr(self):
        return {
            "type": "not",
            "field": self.mBaseCond.getDruidRepr()}

#===============================================
class _XL_Joiner(XL_Condition):
    def __init__(self, items):
        XL_Condition.__init__(self)
        self.mItems = items
        assert len(self.mItems) > 0

    def getItems(self):
        return self.mItems

    def getDruidRepr(self):
        return {
            "type": self.getCondKind(),
            "fields": [cond.getDruidRepr() for cond in self.mItems]}

#===============================================
class XL_And(_XL_Joiner):
    def __init__(self, items):
        _XL_Joiner.__init__(self, items)

    def getCondKind(self):
        return "and"

    def addAnd(self, other):
        if other.getCondKind() == "and":
            add_items = other.getItems()
        else:
            add_items = [other]
        return XL_And(self.getItems() + add_items)

#===============================================
class XL_Or(_XL_Joiner):
    def __init__(self, items):
        _XL_Joiner.__init__(self, items)

    def getCondKind(self):
        return "or"

    def addOr(self, other):
        if other.getCondKind() == "or":
            add_items = other.getItems()
        else:
            add_items = [other]
        return XL_Or(self.getItems() + add_items)

#===============================================
class XL_None(XL_Condition):
    def __init__(self):
        XL_Condition.__init__(self)

    def addAnd(self, other):
        return self

    def addOr(self, other):
        return other

    def negative(self):
        return XL_All()

    def getCondKind(self):
        return "null"

    def getDruidRepr(self):
        return False

#===============================================
class XL_All(XL_Condition):
    def __init__(self):
        XL_Condition.__init__(self)

    def addAnd(self, other):
        return other

    def addOr(self, other):
        return self

    def negative(self):
        return XL_None()

    def getCondKind(self):
        return "all"

    def getDruidRepr(self):
        return None

#===============================================

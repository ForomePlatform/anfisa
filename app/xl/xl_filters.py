#===============================================
class _FltContainer:
    def __init__(self, type = "and"):
        self.mType  = type
        self.mItems = []

    def sameType(self, other):
        return self.mType == other.mType

    def add(self, item):
        if item is not None:
            self.mItems.append(item)

    def _seqResult(self):
        ret = []
        for item in self.mItems:
            if isinstance(item, dict):
                ret.append(item)
                continue
            if self.sameType(item):
               ret += item._seqResult()
               continue
            res = item.result()
            if res is not None:
                ret.append(res)
        return ret

    def result(self):
        seq = self._seqResult()
        if len(seq) == 0:
            return None
        if len(seq) == 1:
            return seq[0]
        return {"type": self.mType, "fields": seq}

#===============================================
class XL_Filter:
    @classmethod
    def makeFilter(cls, conditions):
        if not conditions:
            return None
        joiner = _FltContainer("and")
        for cond_info in conditions:
            joiner.add(cls.oneCond(cond_info))
        return joiner.result()

    @classmethod
    def oneCond(cls, cond_info):
        if cond_info[0] == "numeric":
            unit_name, ge_mode, the_val, use_undef = cond_info[1:]
            return cls.numericCond(unit_name, ge_mode, the_val, use_undef)
        if cond_info[0] == "enum":
            unit_name, filter_mode, variants = cond_info[1:]
            return cls.enumCond(unit_name, filter_mode, variants)

    @classmethod
    def numericCond(cls, unit_name, ge_mode, the_val, use_undef):
        # use_undef ignored
        if ge_mode > 0:
            return {
                "type": "bound",
                "dimension": unit_name,
                "upper": str(the_val),
                "upperStrict": False,
                "ordering": "numeric" }
        if ge_mode == 0:
            return {
                "type": "bound",
                "dimension": unit_name,
                "lower": str(the_val),
                "lowerStrict": False,
                "ordering": "numeric" }
        return None

    @classmethod
    def enumCond(cls, unit_name, filter_mode, variants):
        if filter_mode == "ONLY":
            return None
        joiner = _FltContainer("or" if filter_mode == "" else "and")
        for val in variants:
            item = {
                "type": "selector",
                "dimension": unit_name,
                "value": val }
            if filter_mode == "NOT":
                item = {
                    "type": "not",
                    "field": item}
            joiner.add(item)
        return joiner

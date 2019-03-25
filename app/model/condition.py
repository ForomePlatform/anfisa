#===============================================
class ConditionMaker:
    @staticmethod
    def condNum(unit_name, bounds, use_undef = False):
        return ["numeric", unit_name, bounds, use_undef]

    @staticmethod
    def condEnum(unit_name, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "ONLY", "NOT"}
        return ["enum", unit_name, join_mode, variants]

    @staticmethod
    def upgradeOldFormat(cond_data):
        if cond_data[0] in {"int", "float"}:
            cond_data[0] = "numeric"
        if cond_data[0] == "status":
            cond_data[0] = "enum"
        if cond_data[0] == "numeric" and len(cond_data) == 5:
            unit_name, upper_bound_mode, bound, use_undef = cond_data[1:]
            bounds = [None, bound] if upper_bound_mode else [bound, None]
            return ["numeric", unit_name, bounds, use_undef]
        return cond_data

    @classmethod
    def upgradeOldFormatSeq(cls, cond_seq):
        return [cls.upgradeOldFormat(cond_data) for cond_data in cond_seq]

#===============================================

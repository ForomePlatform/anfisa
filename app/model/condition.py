#===============================================
class ConditionMaker:
    @staticmethod
    def condNumUpperBound(unit_name, bound, use_undef = False):
        return ["numeric", unit_name, 1, bound, use_undef]

    @staticmethod
    def condNumLowerBound(unit_name, bound, use_undef = False):
        return ["numeric", unit_name, 0, bound, use_undef]

    @staticmethod
    def condEnum(unit_name, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "ONLY", "NOT"}
        return ["enum", unit_name, join_mode, variants]

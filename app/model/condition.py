#===============================================
class ConditionMaker:
    @staticmethod
    def condNumGE(unit_name, bound, use_undef = False):
        return ["numeric", unit_name, True, bound, use_undef]

    @staticmethod
    def condNumLE(unit_name, bound, use_undef = False):
        return ["numeric", unit_name, False, bound, use_undef]

    @staticmethod
    def condEnum(unit_name, variants, join_mode = "OR"):
        assert join_mode in {"AND", "OR", "ONLY", "NOT"}
        return ["enum", unit_name, join_mode, variants]

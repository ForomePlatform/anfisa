from app.search.condition import ConditionMaker

#===============================================
class XL_Setup:
    sFilters = dict()

    @classmethod
    def regFilter(cls, flt_name, conditions):
        cls.sFilters[flt_name] = conditions

    @classmethod
    def getFilterNames(cls):
        return cls.sFilters.keys()

    @classmethod
    def hasFilter(cls, flt_name):
        return flt_name in cls.sFilters

    @classmethod
    def getFilterConditions(cls, flt_name):
        return cls.sFilters.get(flt_name)

#===============================================
def initXL():
    XL_Setup.regFilter("Candidates_BGM",
        [ConditionMaker.condEnum("Rules", ["Candidates_BGM"])])
    XL_Setup.regFilter("SEQaBOO_Hearing_Loss_v_01",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_01"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    XL_Setup.regFilter("SEQaBOO_Hearing_Loss_v_02",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_02"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    XL_Setup.regFilter("SEQaBOO_Hearing_Loss_v_03",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")
        ])
    XL_Setup.regFilter("SEQaBOO_ACMG59",
        [
            ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
            ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")
        ])

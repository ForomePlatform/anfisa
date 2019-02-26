from .condition import ConditionMaker

#===============================================
STD_WS_FILTERS = {
    "Candidates_BGM": [
        ConditionMaker.condEnum("Rules", ["Candidates_BGM"])],
    "SEQaBOO_Hearing_Loss_v_01": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_01"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
    "SEQaBOO_Hearing_Loss_v_02": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_02"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
    "SEQaBOO_Hearing_Loss_v_03": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")],
    "SEQaBOO_ACMG59": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")]}

#===============================================
STD_XL_FILTERS = {}

import os, codecs
from app.filter.condition import ConditionMaker

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
    "SEQaBOO_Hearing_Loss_v_03_5": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Rules", ["HL_All_Genes"])],
    "SEQaBOO_ACMG59": [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")]}

#===============================================
STD_XL_FILTERS = {}

#===============================================
def loadConfigFile(fname):
    with codecs.open(os.path.dirname(os.path.abspath(__file__)) +
            "/files/" + fname, "r", encoding = "utf-8") as inp:
        return inp.read()

def loadConfigFileSeq(fnames):
    return "\n".join([loadConfigFile(fname) for fname in fnames])

#===============================================
STD_TREE_CODE_SEQ = [
    ["BGM Candidates", loadConfigFileSeq(
        ["quality.pyt", "inheritance.pyt", "rare.pyt"])],
    ["All Rare Variants", loadConfigFileSeq(
        ["quality.pyt", "rare.pyt"])],
    ["Hearing Loss", loadConfigFileSeq(
        ["quality.pyt", "hearing_loss.pyt"])]
]

#===============================================

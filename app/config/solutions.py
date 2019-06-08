import os, codecs
from md5 import md5

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
    ["Q Test", loadConfigFileSeq(["quality.pyt", "return_true.pyt"])],
    ["R Test", loadConfigFileSeq(["rare.pyt", "return_true.pyt"])],
    ["T Test", loadConfigFile("trio.pyt")],
    ["H Test", loadConfigFile("hearing_loss.pyt")],
    ["Trio Candidates", loadConfigFileSeq(
        ["quality.pyt", "rare.pyt", "trio.pyt"])],
    ["All Rare Variants", loadConfigFileSeq(
        ["quality.pyt", "rare.pyt", "return_true.pyt"])],
    ["Hearing Loss", loadConfigFileSeq(
        ["quality.pyt", "hearing_loss.pyt"])]
]

#===============================================
def loadListFile(fname):
    ret = []
    with codecs.open(os.path.dirname(os.path.abspath(__file__)) +
            "/files/" + fname, "r", encoding = "utf-8") as inp:
        for line in inp:
            val = line.partition('#')[0].strip()
            if val:
                ret.append(val)
    return ret

#===============================================
STD_ENUM_PANNELS = {
    "Genes": {
        "ACMG59": loadListFile("acmg59.lst"),
        "All_Hearing_Loss":  loadListFile("all_hearing_loss.lst"),
        "Reportable_Hearing_Loss": loadListFile("rep_hearing_loss.lst")
    }
}

STD_ENUM_PANNELS_REF = {
    unit_name: sorted([key for key, value in unit_dict.items()])
    for unit_name, unit_dict in STD_ENUM_PANNELS.items()}

#===============================================
def codeHash(tree_code):
    return md5(tree_code.strip()).hexdigest()

#===============================================
class StdTreeCodes:
    sKeys = [key for key, code in STD_TREE_CODE_SEQ]
    sCodes = {key: (code, codeHash(code))
        for key, code in STD_TREE_CODE_SEQ}
    sHashCodes = {info[1]: key for key, info in sCodes.items()}

    @classmethod
    def getKeys(cls):
        return cls.sKeys

    @classmethod
    def getCode(cls, key = None):
        if key is None:
            key = cls.sKeys[0]
        return cls.sCodes[key][0]

    @classmethod
    def getKeyByHash(cls, hash_code):
        return cls.sHashCodes.get(hash_code)

#===============================================
class Solutions:
    @staticmethod
    def report():
        global STD_ENUM_PANNELS_REF
        return {
            "codes": StdTreeCodes.getKeys(),
            "panels": STD_ENUM_PANNELS_REF}

    @staticmethod
    def getWsFilters():
        global STD_WS_FILTERS
        return STD_WS_FILTERS.items()

    @staticmethod
    def getXlFilters():
        global STD_XL_FILTERS
        return STD_XL_FILTERS.items()

    @staticmethod
    def getPanel(unit_name, panel_name):
        global STD_ENUM_PANNELS
        return STD_ENUM_PANNELS.get(unit_name, dict()).get(panel_name)

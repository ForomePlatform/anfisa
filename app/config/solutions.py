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
    ["BGM Candidates", loadConfigFileSeq(
        ["quality.pyt", "inheritance.pyt", "rare.pyt"])],
    ["All Rare Variants", loadConfigFileSeq(
        ["quality.pyt", "rare.pyt"])],
    ["Hearing Loss", loadConfigFileSeq(
        ["quality.pyt", "hearing_loss.pyt"])]
]

#===============================================
STD_ENUM_PANNELS = {
    "Genes": {
        "ACMG59": [
            "TMEM43",
            "DSP",
            "PKP2",
            "DSG2",
            "DSC2",
            "BRCA1",
            "BRCA2",
            "RYR2",
            "LMNA",
            "COL3A1",
            "GLA",
            "APC",
            "MUTYH",
            "APOB",
            "LDLR",
            "MYH7",
            "TPM1",
            "MYBPC3",
            "PRKAG2",
            "TNNI3",
            "MYL3",
            "MYL2",
            "ACTC1",
            "PCSK9",
            "BMPR1A",
            "SMAD4",
            "TNNT2",
            "TP53",
            "TGFBR1",
            "TGFBR2",
            "SMAD3",
            "KCNQ1",
            "KCNH1",
            "SCN5A",
            "MLH1",
            "MSH2",
            "MSH6",
            "PMS2",
            "RYR1",
            "CACNA1S",
            "FBN1",
            "MEN1",
            "RET",
            "NF2",
            "OTC",
            "SDHD",
            "SDHAF2",
            "SDHC",
            "SDHB",
            "STK11",
            "PTEN",
            "RB1",
            "MYH11",
            "ACTA2",
            "TSC1",
            "TSC2",
            "VHL",
            "WT1",
            "ATP7B"]
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
        return STD_WS_FILTERS

    @staticmethod
    def getXlFilters():
        global STD_XL_FILTERS
        return STD_XL_FILTERS

    @staticmethod
    def getPanel(unit_name, panel_name):
        global STD_ENUM_PANNELS
        return STD_ENUM_PANNELS.get(unit_name, dict()).get(panel_name)

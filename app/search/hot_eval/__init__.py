import os, codecs

from .acmg59 import evalRec as acmg59_evalRec
from .hl_reportable import evalRec as hl_reportable_evalRec
from .quality_check import evalRec as quality_check_evalRec
from .af_check import evalRec as af_check_evalRec
from .bgm_rule import evalRec as bgm_rule_evalRec
from .seq_a_boo_hearing_loss import evalRec as seq_a_boo_hearing_loss_evalRec
from .seq_a_boo_hearing_loss_2 import evalRec as seq_a_boo_hearing_loss_2_evalRec
from .seq_a_boo_acmg59 import evalRec as seq_a_boo_acmg59_evalRec
from .common_check import evalRec as common_check_evalRec
from .polyphen_check import evalRec as polyphen_check_evalRec

#===============================================
class RuleFuncH:
    def __init__(self, name, filename, function, research_mode = False):
        self.mName      = name
        self.mFileName  = filename
        self.mFunc      = function
        self.mIsResearch  = research_mode

    def getFileName(self):
        return self.mFileName

    def getName(self):
        return self.mName

    def getFunc(self):
        return self.mFunc

    def isResearch(self):
        return self.mIsResearch

#===============================================
class RuleParamH:
    def __init__(self, name, value, research_mode = False):
        self.mName      = name
        self.mValue     = value
        self.mIsResearch  = research_mode

    def getName(self):
        return self.mName

    def getValue(self):
        return self.mValue

    def setValue(self, value):
        self.mValue = value

    def isResearch(self):
        return self.mIsResearch

#===============================================
class HOT_SETUP:
    sPath = os.path.dirname(os.path.abspath(__file__))

    FUNCTIONS = [
        RuleFuncH("ACMG59",
            "acmg59", acmg59_evalRec),
        RuleFuncH("HL_Reportable_Genes",
            "hl_reportable", hl_reportable_evalRec),
        RuleFuncH("Quality-PASS",
            "quality_check", quality_check_evalRec),
        RuleFuncH("Candidates_BGM",
            "bgm_rule", bgm_rule_evalRec),
        RuleFuncH("SEQaBOO_Hearing_Loss_v_02",
            "seq_a_boo_hearing_loss_v02", seq_a_boo_hearing_loss_evalRec),
        RuleFuncH("SEQaBOO_Hearing_Loss_v_01",
            "seq_a_boo_hearing_loss_v01", seq_a_boo_hearing_loss_2_evalRec),
        RuleFuncH("SEQaBOO_ACMG59",
            "seq_a_boo_acmg59", seq_a_boo_acmg59_evalRec),
        RuleFuncH("gnomAD_Frequency_Threshold",
            "af_check", af_check_evalRec),
        RuleFuncH("Has_Damaging_Predictions",
            "polyphen_check", polyphen_check_evalRec)
        # RuleFuncH("SEQaBOO_Hearing_Loss_2",
        #           "seq_a_boo_hearing_loss_2", seq_a_boo_hearing_loss_2_evalRec),
        # RuleFuncH("Candidates_Including_Common",
        #           "common_check", common_check_evalRec)
    ]

    PARAMETERS = [
        RuleParamH("exon_dist", 5),
        RuleParamH("af", 0.01),
        RuleParamH("af_seq_a_boo", 0.0007),
        RuleParamH("af_popmax", 0.01),
        RuleParamH("an_popmax", 2000),
        RuleParamH("af_in_db", 0.05),
        RuleParamH("severity", 1),
        RuleParamH("gq", 20),
        RuleParamH("fs", 30),
        RuleParamH("qd", 4)]

    @classmethod
    def getSrcContent(cls, key):
        with codecs.open(cls.sPath + "/" + key + ".py",
                "r", encoding = "utf-8") as inp:
            return inp.read()

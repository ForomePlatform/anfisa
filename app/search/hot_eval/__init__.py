import os, codecs

from .acmg59 import evalRec as acmg59_evalRec
from .af_check import evalRec as af_check_evalRec
from .rare_check   import evalRec as rare_check_evalRec
from .common_check import evalRec as common_check_evalRec
from .polyphen_check import evalRec as polyphen_check_evalRec

#===============================================
class HOT_SETUP:
    sPath = os.path.dirname(os.path.abspath(__file__))

    FUNCTIONS = [
        # title, function, name, expert_mode
        ("ACMG59", acmg59_evalRec,
            "acmg59", False),
        ("Candidates (Rare)", rare_check_evalRec,
            "rare_check", False),
        ("Candidates (Clinical)", common_check_evalRec,
            "common_check", False),
        ("gnomAD Frequency Threshold", af_check_evalRec,
            "af_check", False),
        ("Has Damaging Predictions", polyphen_check_evalRec,
            "polyphen_check", False)
    ]

    ATTRIBUTES = [
        ("af", 0.01, False),
        ("af_in_db", 0.05, False),
        ("severity", 0, False),
        ("gq", 20, False),
        ("fs", 30, False),
        ("qd", 4, False)]

    @classmethod
    def getSrcContent(cls, key):
        with codecs.open(cls.sPath + "/" + key + ".py",
                "r", encoding = "utf-8") as inp:
            return inp.read()

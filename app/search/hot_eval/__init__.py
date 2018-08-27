import os, codecs

from .acmg59 import evalRec as acmg59_evalRec
from .af_check import evalRec as af_check_evalRec
from .rare_check import evalRec as rare_check_evalRec
from .polyphen_check import evalRec as polyphen_check_evalRec

#===============================================
class HOT_SETUP:
    sPath = os.path.dirname(os.path.abspath(__file__))

    FUNCTIONS = [
        # name, function, expert_mode
        ("acmg59", acmg59_evalRec, False),
        ("af_check", af_check_evalRec, False),
        ("rare_check", rare_check_evalRec, False),
        ("polyphen_check", polyphen_check_evalRec, False)]

    ATTRIBUTES = [
        ("af", 0.01, False),
        ("af_in_db", 0.05, False),
        ("gq", 20, False),
        ("fs", 30, False),
        ("qd", 4, False)]

    @classmethod
    def getSrcContent(cls, key):
        with codecs.open(cls.sPath + "/" + key + ".py",
                "r", encoding = "utf-8") as inp:
            return inp.read()

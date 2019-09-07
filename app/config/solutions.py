import os
from app.filter.condition import ConditionMaker
from app.filter.sol_pack import SolutionPack
#===============================================
sCfgFilePath = os.path.dirname(os.path.abspath(__file__)) + "/files/"

def cfgPath(fname):
    global sCfgFilePath
    return sCfgFilePath + fname

def cfgPathSeq(fnames):
    return [cfgPath(fname) for fname in fnames]

#===============================================
sSolutionsAreSet = False
def prepareSolutions():
    global sSolutionsAreSet
    if sSolutionsAreSet:
        return
    sSolutionsAreSet = True
    base_pack = SolutionPack("BASE")
    SolutionPack.regDefaultPack(base_pack)
    SolutionPack.regPack(base_pack)

    base_pack.regFilterWS("Candidates_BGM", [
        ConditionMaker.condEnum("Rules", ["Candidates_BGM"])])
    base_pack.regFilterWS("SEQaBOO_Hearing_Loss_v_01", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_01"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")])
    base_pack.regFilterWS("SEQaBOO_Hearing_Loss_v_02", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_02"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")])
    base_pack.regFilterWS("SEQaBOO_Hearing_Loss_v_03", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "NOT")])
    base_pack.regFilterWS("SEQaBOO_Hearing_Loss_v_03_5", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_Hearing_Loss_v_03"]),
        ConditionMaker.condEnum("Panels", ["All_Hearing_Loss"])])
    base_pack.regFilterWS("SEQaBOO_ACMG59", [
        ConditionMaker.condEnum("Rules", ["SEQaBOO_ACMG59"]),
        ConditionMaker.condEnum("Rules", ["ACMG59"], "AND")])

    #base_pack.regFilterXL(?, ?)

    # Production Decision Trees
    base_pack.regTreeCode("BGM xBrowse Alt",
        cfgPathSeq(["bgm_xbrowse.pyt"]),
        requires = {"trio_base"})
    base_pack.regTreeCode("Trio Candidates",
        cfgPathSeq(["quality.pyt", "rare.pyt", "trio.pyt"]),
        requires = {"trio_base"})
    base_pack.regTreeCode("All Rare Variants",
        cfgPathSeq(["quality.pyt", "rare.pyt", "return_true.pyt"]))
    base_pack.regTreeCode("Hearing Loss, v.4",
        cfgPathSeq(["quality.pyt", "hearing_loss.pyt"]))
    base_pack.regTreeCode("Hearing Loss, v.2",
        cfgPathSeq(["quality.pyt", "hearing_loss_v2.pyt"]))
    base_pack.regTreeCode("ACMG59",
        cfgPathSeq(["quality.pyt", "acmg59.pyt"]))

    # Test trees
    # base_pack.regTreeCode("Q Test",
    #     cfgPathSeq(["quality.pyt", "return_true.pyt"]))
    # base_pack.regTreeCode("R Test",
    #     cfgPathSeq(["rare.pyt", "return_true.pyt"]))
    # base_pack.regTreeCode("T Test",
    #     [cfgPath("trio.pyt")],
    #     requires = {"trio_base"})
    # base_pack.regTreeCode("H Test",
    #     [cfgPath("hearing_loss.pyt")])

    base_pack.regPanel("Symbol", "ACMG59",
        cfgPath("acmg59.lst"))
    base_pack.regPanel("Symbol", "All_Hearing_Loss",
        cfgPath("all_hearing_loss.lst"))
    base_pack.regPanel("Symbol", "Reportable_Hearing_Loss",
        cfgPath("rep_hearing_loss.lst"))


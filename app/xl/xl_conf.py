from app.model.condition import ConditionMaker
from .decision import DecisionTree
#===============================================
def defineDefaultDecisionTree(cond_env):
    return defineHearingLossTree(cond_env)
    #return defineBGMTree(cond_env)


def defineHearingLossTree(cond_env):
    dtree = DecisionTree(cond_env)

    addQuality(dtree)

    dtree.addComment(
        '1.	    Include if present in HGMD as "DM"')
    dtree.addCondition(
        ConditionMaker.condEnum("HGMD_Tags", ["DM"]),
        decision = True)

    dtree.addComment(
        '2.	    Exclude unless AF < 5% AND +/- bases from intronic/exonic border')
    dtree.addCondition(
        ConditionMaker.condNum("gnomAD_AF", [0.05, None]),
        decision = False)
    dtree.addCondition(["and",
        ConditionMaker.condNum("Dist_from_Exon", [6, None]),
        ConditionMaker.condEnum("Region", ["exon"], "NOT")],
        decision = False)

    dtree.addComment(
        '2.a.	Include if present in ClinVar Path, Likely Path, VUS (worst annotation), unless annotated benign by trusted submitter')
    dtree.addCondition(["and",
        ConditionMaker.condEnum("Clinvar_Benign", ["True"]),
        ConditionMaker.condEnum("Clinvar_Trusted_Benign",
            ["False", "No data"])],
        decision = True)

    dtree.addComment(
        '2.b.	Include all de-novo variants')
    dtree.addCondition(
        ConditionMaker.condEnum("Callers", ["BGM_BAYES_DE_NOVO"]),
        decision = True)

    dtree.addComment(
        '2.c.	Include all potential LOF variants '
        '(stop-codon, frameshift, canonical splice site).')

    dtree.addCondition(
        ConditionMaker.condNum("Severity", [3, None]),
        decision = True)

    dtree.addComment(
        '3.a.	For the rest: exclude "Missense", "synonymous" '
        'and "splice region" variants')
    dtree.addCondition(
        ConditionMaker.condNum("Severity", [None, 0]),
        decision = False)

    dtree.addComment(
        '3.	Include: AF < 0.0007 (GnomAD Overall) AND +/- 5 bases')
    dtree.addComment(
        'And: PopMax < 0.01 (minimum 2000 alleles total in ancestral group)')
    dtree.addCondition(["and",
        ConditionMaker.condNum("gnomAD_AF", [None, 0.0007]),
        ["or",
            ConditionMaker.condNum("gnomAD_PopMax_AN", [None, 2000]),
            ConditionMaker.condNum("gnomAD_PopMax_AF", [None, 0.01])]],
        decision = True)
    dtree.setFinalDecision(False)

    return dtree


def defineBGMTree(cond_env):
    dtree = DecisionTree(cond_env)
    addQuality(dtree)

    dtree.addComment("Exclude common variants")
    dtree.addCondition(
        ConditionMaker.condNum("gnomAD_AF", [0.001, None]),
        decision = False
    )

    dtree.addComment("Exclude low impact variants")
    dtree.addCondition(
        ConditionMaker.condNum("Severity", [None, 0]),
        decision = False
    )

    dtree.setFinalDecision(True)

    return dtree


def addQuality(dtree):
    dtree.addComment(
        "0.     Check sequencing quality")
    dtree.addCondition(
        ConditionMaker.condNum("Proband_GQ", [None, 19]),
        decision = False)
    dtree.addCondition(
        ConditionMaker.condNum("FS", [31, None]),
        decision = False)
    dtree.addCondition(
        ConditionMaker.condNum("QD", [None, 3]),
        decision = False)

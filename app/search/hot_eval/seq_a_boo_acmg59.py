def evalRec(env, rec):
    """SEQaBOO ACMG59 Rule"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM", "DM?"}) > 0
    clinvar_clinically_significant = (rec.Clinvar_Benign == False)
    clinically_significant = clinvar_clinically_significant or hdmd_clinically_significant

    if (clinically_significant):
        return True

    if (rec.Severity > 2):
        return True

    return False
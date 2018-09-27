def evalRec(env, rec):
    """SEQaBOO Rule"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    if (rec.Clinvar_Benign == True or rec.HGMD_Benign == True):
        return False

    if (rec.Severity <1):
        return False

    if (rec.Severity == 1 and len(rec.ClinVar_Significance) == 0):
        return False

    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if (known):
        min_frequency = env.af_in_db
    else:
        min_frequency = env.af
    return rec.gnomAD_AF < min_frequency

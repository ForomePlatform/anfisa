def evalRec(env, rec):
    """SEQaBOO Rule"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    # ========== Always want ===============:
    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0
    clinically_significant = rec.Clinvar_Benign == False or rec.HGMD_Benign == False

    if (clinically_significant):
        return True

    if (rec.Severity > 2):
        return True

    if ("DM" in rec.HGMD_Tags):
        return True

    return False
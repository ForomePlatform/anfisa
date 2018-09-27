def evalRec(env, rec):
    """Candidates (Clinical)"""

    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if ("Quality-PASS" not in rec.Rules):
        return False



    if (known):
        return True
    if (rec.Severity < env.severity):
        return False
    return rec.gnomAD_AF < env.af

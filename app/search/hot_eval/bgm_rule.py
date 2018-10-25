def evalRec(env, rec):
    """BGM Acceptance Filter"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    if (len(rec.Has_Variant & {"proband"}) == 0):
        return False

    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if (known):
        min_frequency = env.af_in_db
    else:
        min_frequency = env.af
    return rec.gnomAD_AF_Proband < min_frequency

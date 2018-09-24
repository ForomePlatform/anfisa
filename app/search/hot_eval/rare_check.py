def evalRec(env, rec):
    """Candidates (Rare)"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if (known):
        min_frequency = env.af_in_db
    else:
        min_frequency = env.af
    return rec.gnomAD_AF < min_frequency

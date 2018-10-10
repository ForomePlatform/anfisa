def evalRec(env, rec):
    """SEQaBOO Rule"""

    # Quality
    if ("Quality-PASS" not in rec.Rules):
        return False

    # Discard common variants
    if (rec.gnomAD_AF_Exomes > env.af_in_db):
        return False

    # ========== Always want ===============:
    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0
    hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM", "DM?"}) > 0
    ## or rec.HGMD_Benign == False
    clinvar_clinically_significant = (rec.Clinvar_Benign == False)
    clinically_significant = clinvar_clinically_significant or hdmd_clinically_significant

    if (clinically_significant):
        return True

    if (rec.Severity > 2):
        return True

    if ("BGM_BAYES_DE_NOVO" in rec.Callers):
        return True

    # ================ Applying rules ==============
    if (rec.Severity < 1):
        return False

    min_frequency = env.af_seq_a_boo
    return rec.gnomAD_AF_Exomes < min_frequency

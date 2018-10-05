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

    if ("BGM_BAYES_DE_NOVO" in rec.Callers):
        return True

    # ================ Applying rules ==============
    if (rec.Severity < 1):
        return False

    min_frequency = env.af_seq_a_boo
    return rec.gnomAD_AF < min_frequency

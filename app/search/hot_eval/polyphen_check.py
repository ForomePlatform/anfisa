def evalRec(env, rec):
    """Has Damaging Predictions"""

    if (rec.Severity > 2):
        return True

    # 2.a.	Present in ClinVar Path, Likely Path, VUS (worst annotation).
    clinvar_clinically_significant = (rec.Clinvar_Benign == False) \
        and (rec.Clinvar_Trusted_Benign in {False, "No data"})
    if (clinvar_clinically_significant):
        return True

    # Include Splice Altering variants
    if (rec.splice_ai_dsmax > 0.2):
        return True

    if len(rec.Polyphen &
            {"possibly_damaging", "probably_damaging"}) > 0:
        return True
    if (len(rec.Polyphen_2_HVAR) > 0 and
            len(rec.Polyphen_2_HVAR - {"P", "D"}) == 0):
        return True
    if (len(rec.Polyphen_2_HDIV) > 0 and
            len(rec.Polyphen_2_HDIV - {"P", "D"}) == 0):
        return True
    return len(rec.SIFT &
        {"deleterious", "tolerated_low_confidence"}) > 0

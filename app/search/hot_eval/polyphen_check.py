def evalRec(env, rec):
    if len(rec.Polyphen & {"possibly_damaging", "probably_damaging"}) > 0:
        return True
    if (len(rec.Polyphen_2_HVAR) > 0 and
            len(rec.Polyphen_2_HVAR - {"P", "D"}) == 0):
        return True
    if (len(rec.Polyphen_2_HDIV) > 0 and
            len(rec.Polyphen_2_HDIV - {"P", "D"}) == 0):
        return True
    return len(rec.SIFT & {"deleterious", "tolerated_low_confidence"}) > 0

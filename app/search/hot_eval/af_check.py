def evalRec(env, rec):
    if rec.gnomAD_AF < 0.01:
        return True
    if rec.gnomAD_AF < 0.05:
        return len(rec.db & {"ClinVar", "HGMD"}) > 0

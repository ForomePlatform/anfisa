def evalRec(env, rec):
    if not rec.Proband_has_Variant:
        return False
    if rec.Proband_GQ < env.gq:
        return False
    if rec.FS > env.fs:
        return False
    if rec.QD < env.qd:
        return False
    if rec.gnomAD_AF < env.af:
        return True
    if rec.gnomAD_AF < env.af_in_db:
        return len(rec.db & {"ClinVar", "HGMD"}) > 0

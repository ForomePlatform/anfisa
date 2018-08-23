def evalRec(rec, af = 0.01, af_in_db = 0.05, gq = 20, fs = 30, dp = 4):
    if not rec.Proband_has_Variant:
        return False
    if rec.Proband_GQ < gq:
        return False
    if rec.FS > fs:
        return False
    if rec.DP < dp:
        return False
    if rec.gnomAD_AF < af:
        return True
    if rec.gnomAD_AF < af_in_db:
        return len(rec.db & {"ClinVar", "HGMD"}) > 0

def evalRec(env, rec):
    quality = True
    if not rec.Proband_has_Variant:
        quality = False
    elif rec.Proband_GQ < env.gq:
        quality = False
    elif rec.FS > env.fs:
        quality = False
    elif rec.QD < env.qd:
        quality = False
    known = len(rec.Presence_in_Databases & {"ClinVar", "HGMD"}) > 0

    if (not quality):
        return False
    if (known):
        return True
    if (rec.Severity < env.severity):
        return False
    return rec.gnomAD_AF < env.af

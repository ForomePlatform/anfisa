def evalRec(env, rec):
    # standard part of evaluation
    quality = True
    if not rec.Proband_has_Variant:
        quality = False
    elif rec.Proband_GQ < env.gq:
        quality = False
    elif rec.FS > env.fs:
        quality = False
    elif rec.QD < env.qd:
        quality = False
    known = len(rec.db & {"ClinVar", "HGMD"}) > 0

    # "rare" variant of check evaluation
    if (not quality):
        return False
    if (known):
        min_frequency = env.af_in_db
    else:
        min_frequency = env.af
    return rec.gnomAD_AF < min_frequency

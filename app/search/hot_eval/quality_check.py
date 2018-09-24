def evalRec(env, rec):
    """Quality check"""

    if rec.Proband_GQ < env.gq:
        return False
    elif rec.FS > env.fs:
        return False
    elif rec.QD < env.qd:
        return False
    return True

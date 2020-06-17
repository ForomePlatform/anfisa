#0.     Check sequencing quality
if Proband_GQ <= 19:
    return False
if FS > 30:
    return False
if QD < 4:
    return False

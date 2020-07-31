#0.     Check sequencing quality
if Min_GQ <= 19:
    return False
if FS > 30:
    return False
if (0 < QD and QD < 4):
    return False
if (QD <= 0 and 0 < QUAL and QUAL < 40):
    return False

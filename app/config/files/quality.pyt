#0.     Check sequencing quality
if Proband_GQ <= 19:
    return False
if FS >= 30.0001:
    return False
if (0.0001 <= QD and QD <= 4):
    return False

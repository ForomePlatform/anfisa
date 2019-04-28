#0.     Check sequencing quality
if Proband_GQ <= 19:
    return False
if FS >= 31:
    return False
if QD <= 3:
    return False


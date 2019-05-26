#0.     Check sequencing quality
if Proband_GQ <= 19:
    return False
if FS >= 30.0001:
    return False
if QD <= 3.99999:
    return False

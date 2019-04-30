#Exclude common variants
if gnomAD_AF >= 0.001:
    return False
    
#Exclude low impact variants
if Severity <= 0:
    return False

return True

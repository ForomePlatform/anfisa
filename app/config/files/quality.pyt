#0.     Check sequencing quality
#0.     Check sequencing quality
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if Min_GQ < 20:
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if FS > 30:
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (0 < QD and QD < 4):
    return False
"""
@knowledge_domain("Call Annotations")
@scale("Variant")
"""
if (QD < 0 and 0 < QUAL and QUAL < 40):
    return False

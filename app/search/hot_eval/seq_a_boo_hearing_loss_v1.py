def evalRec(env, rec):
    """SEQaBOO Rule for Hearing Loss Genes"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    # 1.	Present in HGMD as "DM" or "DM?"
    hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM", "DM?"}) > 0
    if hdmd_clinically_significant:
        return True

    # 2.	AF< 5% AND +/- bases from intronic/exonic border
    if (rec.gnomAD_AF_Exomes > env.af_in_db):
        return False
    if (rec.Dist_from_Exon > env.exon_dist and rec.Region != "exon"):
        return False

    # 2.a.	Present in ClinVar Path, Likely Path, VUS (worst annotation).
    clinvar_clinically_significant = (rec.Clinvar_Benign == False)
    if (clinvar_clinically_significant):
        return True

    # 2.b.	All de novo variants
    if ("BGM_BAYES_DE_NOVO" in rec.Callers):
        return True

    # 2.c.	All potential LOF variants (stop-codon, frameshift, canonical splice site).
    if (rec.Severity > 2):
        return True

    # 3.a.	annotated as "Missense", "synonymous" and "splice region" variants
    if (rec.Severity < 1):
        return False

    # 3.	AF < 0.0007 (GnomAD Exome) AND +/- 5 bases
    min_frequency = env.af_seq_a_boo
    return rec.gnomAD_AF_Exomes < min_frequency


# Inclusion criteria for SEQaBOO gene list:
# 1.	Present in HGMD as "DM" or "DM?"
#
# 2.	AF< 5% AND +/- bases from intronic/exonic border
# a.	Present in ClinVar Path, Likely Path, VUS (worst annotation).
# b.	All de novo variants
# c.	All potential LOF variants (stop-codon, frameshift, canonical splice site).
#
# 3.	AF < 0.0007 (GnomAD Exome) AND +/- 5 bases
# a.	annotated as "Missense", "synonymous" and "splice region" variants  <0.0007

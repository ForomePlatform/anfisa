def evalRec(env, rec):
    """SEQaBOO Rule for Hearing Loss Genes v.0.2
    This version uses all data from gnomAD but a subset from ClinVar (no submitter data)"""

    # standard part of evaluation
    if ("Quality-PASS" not in rec.Rules):
        return False

    # 1.	Present in HGMD as "DM"
    hdmd_clinically_significant = len(set(rec.HGMD_Tags) & {"DM"}) > 0
    if hdmd_clinically_significant:
        return True

    # 2.	AF< 5% AND +/- bases from intronic/exonic border
    if (rec.gnomAD_AF > env.af_in_db):
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

    # 3.	AF < 0.0007 (GnomAD Overall) AND +/- 5 bases
    min_frequency = env.af_seq_a_boo
    ok =  rec.gnomAD_AF < min_frequency

    # PopMax < 0.01 (minimum 2000 alleles total in ancestral group)
    if (ok and rec.gnomAD_PopMax_AN > env.an_popmax):
        ok = rec.gnomAD_PopMax_AF < env.af_popmax

    return ok


# Present in HGMD as "DM" (NO "DM?")
#
# AF< 5% (gnomAD overall AF) AND +/- 5 bases from intronic/exonic border
# Present in ClinVar Path, Likely Path, VUS (worst annotation).
# All de novo variants
# All potential LOF variants (stop-codon, frameshift, canonical splice site).
#
# AF < 0.0007 (GnomAD Overall AF) AND PopMax < 0.01 (minimum 2000 alleles total in ancestral group)
# annotated as "Missense", "synonymous" and "splice region" variants  <0.0007
# Exons +/- 5 bases
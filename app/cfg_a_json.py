from .cfg_data import AspectH, AttrH, ColGroupH

#===============================================
Aspect_General = AspectH("view.general",     "General",
    attrs = [
        AttrH("Gene(s)", is_seq = True),
        AttrH("header"),
        AttrH("Ref"),
        AttrH("Alt"),
        AttrH("IGV", kind ="link"),
        AttrH("Proband Genotype"),
        AttrH("Maternal Genotype"),
        AttrH("Paternal Genotype"),
        AttrH("Called by", is_seq = True),
        AttrH("BGM_CMPD_HET"),
        AttrH("Worst Annotation"),
        AttrH("cPos", is_seq = True),
        AttrH("pPos", is_seq = True),
        AttrH("RefSeq Transcript (Canonical)", is_seq = True),
        AttrH("RefSeq Transcript (Worst)", is_seq = True),
        AttrH("Ensembl Transcripts (Canonical)", is_seq = True),
        AttrH("Ensembl Transcripts (Worst)", is_seq = True),
        AttrH("Variant Exon (Canonical)", is_seq = True),
        AttrH("Variant Exon (Worst Annotation)", is_seq = True),
        AttrH("Variant Intron (Worst Annotation)", is_seq = True),
        AttrH("Variant Intron (Canonical)", is_seq = True),
    ])

#===============================================
Aspect_Quality = AspectH("quality_samples",     "Quality",
    json_container = None,
    attrs = [
        AttrH("Title"),
        AttrH("Quality by Depth"),
        AttrH("Mapping Quality"),
        AttrH("Variant Call Quality"),
        AttrH("Strand Odds Ratio"),
        AttrH("Fisher Strand Bias"),
        AttrH("Allelic Depth", is_seq=True),
        AttrH("Read Depth"),
        AttrH("Genotype Quality")
    ],
    col_groups = [ColGroupH("quality.samples", None)],
)

#===============================================
Aspect_gnomAD = AspectH("view.gnomAD",      "gnomAD",
    attrs = [
        AttrH("AF"),
        AttrH("Genome AF"),
        AttrH("Exome AF"),
        AttrH("URL", kind = "link", is_seq=True),
        AttrH("PopMax #1"),
        AttrH("PopMax #2")])

#===============================================
Aspect_Databases = AspectH("view.Databases",   "Databases",
    attrs = [
        AttrH("pLI", is_seq = True),
        AttrH("HGMD"),
        AttrH("HGMD Phenotypes", is_seq=True),
        AttrH("HGMD PMIDs", is_seq=True, kind="link"),
        AttrH("OMIM"),
        AttrH("ClinVar Significance", is_seq=True),
        AttrH("ClinVar", "link")
    ])

#===============================================
Aspect_Predictions = AspectH("view.Predictions", "Predictions",
    attrs = [
        AttrH("Polyphen", is_seq = True),
        AttrH("Polyphen 2 HVAR", is_seq = True),
        AttrH("Polyphen 2 HDIV", is_seq = True),
        AttrH("SIFT", is_seq = True),
        AttrH("REVEL", is_seq = True),
        AttrH("Mutation Taster", is_seq = True),
        AttrH("FATHMM", is_seq = True),
        AttrH("CADD (Phred)", is_seq = True),
        AttrH("CADD (Raw)", is_seq = True),
        AttrH("Mutation Assessor", is_seq=True),
        AttrH("SIFT score", is_seq=True),
        AttrH("Polyphen 2 HVAR score", is_seq=True),
        AttrH("Polyphen 2 HDIV score", is_seq=True),
    ])

#===============================================
Aspect_Genetics = AspectH("view.Genetics",    "Genetics",
    attrs = [
        AttrH("Distance From Intron/Exon Boundary (Worst)", is_seq = True),
        AttrH("Distance From Intron/Exon Boundary (Canonical)", is_seq = True),
        AttrH("Conservation", is_seq = True),
        AttrH("Species with variant"),
        AttrH("Species with other variants"),
        AttrH("MaxEntScan"),
        AttrH("NNSplice"),
        AttrH("Human Splicing Finder")])

#===============================================
Aspect_Inheritance = AspectH("view.Inheritance", "Inheritance",
    ignored = True)

#===============================================
Aspect_TechMainData = AspectH("_main", "VEP<br/>Data", json_container = None,
    attrs = [
        AttrH("label"),
        AttrH("color_code"),
        AttrH("id"),
        AttrH("assembly_name", title = "Assembly"),
        AttrH("seq_region_name"),
        AttrH("start"),
        AttrH("end"),
        AttrH("strand"),
        AttrH(None),
        AttrH("allele_string"),
        AttrH("variant_class"),
        AttrH("most_severe_consequence"),
        AttrH("ClinVar"),
        AttrH("HGMD"),
        AttrH("_private.HGMD_PIMIDs", "json", is_seq = True),
        AttrH("_private.HGMD_phenotypes", "json", is_seq = True),
        AttrH("EXPECTED"),
        AttrH("_private.gnomad_db_genomes_af"),
        AttrH("_private._private.gnomad_db_exomes_af"),
        AttrH("SEQaBOO")], kind = "tech")

#===============================================
Aspect_Consequences = AspectH("cons", "VEP<br/>Transcripts",
    json_container = None,
    attrs = [
        AttrH("amino_acids"),
        AttrH("bam_edit"),
        AttrH("biotype"),
        AttrH("cadd_phred"),
        AttrH("cadd_raw"),
        AttrH("canonical"),
        AttrH("ccds"),
        AttrH("cdna_end"),
        AttrH("cdna_start"),
        AttrH("cds_end"),
        AttrH("cds_start"),
        AttrH("clinvar_clnsig"),
        AttrH("clinvar_rs"),
        AttrH("codons"),
        AttrH("consequence_terms", is_seq = True),
        AttrH("conservation"),
        AttrH("distance"),
        AttrH("domains", "json"),
        AttrH("exacpli"),
        AttrH("exon"),
        AttrH("fathmm_pred"),
        AttrH("fathmm_score"),
        AttrH("flags", is_seq = True),
        AttrH("gene_id"),
        AttrH("gene_pheno"),
        AttrH("gene_symbol"),
        AttrH("gene_symbol_source"),
        AttrH("given_ref"),
        AttrH("gnomad_exomes_ac"),
        AttrH("gnomad_exomes_af"),
        AttrH("gnomad_exomes_an"),
        AttrH("gnomad_exomes_asj_af"),
        AttrH("gnomad_genomes_ac"),
        AttrH("gnomad_genomes_af"),
        AttrH("gnomad_genomes_an"),
        AttrH("gnomad_genomes_asj_af"),
        AttrH("hgnc_id"),
        AttrH("hgvs_offset"),
        AttrH("hgvsc"),
        AttrH("hgvsp"),
        AttrH("high_inf_pos"),
        AttrH("impact"),
        AttrH("intron"),
        AttrH("motif_feature_id"),
        AttrH("motif_name"),
        AttrH("motif_pos"),
        AttrH("motif_score_change"),
        AttrH("mutationassessor_pred"),
        AttrH("mutationassessor_score"),
        AttrH("mutationtaster_pred"),
        AttrH("mutationtaster_score"),
        AttrH("polyphen2_hdiv_pred"),
        AttrH("polyphen2_hdiv_score"),
        AttrH("polyphen2_hvar_pred"),
        AttrH("polyphen2_hvar_score"),
        AttrH("polyphen_prediction"),
        AttrH("polyphen_score"),
        AttrH("protein_end"),
        AttrH("protein_id"),
        AttrH("protein_start"),
        AttrH("regulatory_feature_id"),
        AttrH("revel_score"),
        AttrH("sift_pred"),
        AttrH("sift_prediction"),
        AttrH("sift_score"),
        AttrH("strand"),
        AttrH("source"),
        AttrH("swissprot", is_seq = True),
        AttrH("transcript_id"),
        AttrH("trembl", is_seq = True),
        AttrH("uniparc", is_seq = True),
        AttrH("used_ref"),
        AttrH("variant_allele")],
    col_groups = [
        ColGroupH("intergenic_consequences", "Intergenic"),
        ColGroupH("motif_feature_consequences", "Motif"),
        ColGroupH("regulatory_feature_consequences", "Regulatory"),
        ColGroupH("transcript_consequences", "Transcript")],
    kind = "tech")

#===============================================
Aspect_ColocatedVars = AspectH("colv", "Colocated<br/>Variants",
    json_container = None,
    attrs = [
        AttrH("id"),
        AttrH("start"),
        AttrH("end"),
        AttrH("allele_string", "flex"),
        AttrH("strand"),
        AttrH("pubmed", is_seq = True),
        AttrH("somatic"),
        AttrH("AA"),
        AttrH("AFR"),
        AttrH("AMR"),
        AttrH("EA"),
        AttrH("EAS"),
        AttrH("EUR"),
        AttrH("SAS"),
        AttrH("frequencies", "json"),
        AttrH("phenotype_or_disease"),
        AttrH("seq_region_name"),
        AttrH("clin_sig", is_seq = True)] +
        [AttrH(key, attrs = [key + "_allele", key + "_maf"])
            for key in ("aa", "afr", "amr", "ea", "eas", "eur", "sas",
                "gnomad", "gnomad_afr", "gnomad_amr", "gnomad_asj",
                "gnomad_eas", "gnomad_fin", "gnomad_nfe",
                "gnomad_oth", "gnomad_sas")] +
        [AttrH("minor", attrs = ["minor_allele", "minor_allele_freq"])],
    col_groups = [ColGroupH("colocated_variants", None)],
    kind = "tech")

#===============================================
Aspect_VCF = AspectH("input", "VCF",
    json_container = None, attrs = [AttrH("input")],
    kind = "tech")

#===============================================
CONFIG_AJson = {
    "main_key": "label",
    "view_tabs": [
        Aspect_General, Aspect_Quality, Aspect_gnomAD,
        Aspect_Databases, Aspect_Predictions,
        Aspect_Genetics, Aspect_Inheritance,
        Aspect_Consequences, Aspect_ColocatedVars,
        Aspect_TechMainData, Aspect_VCF],
    "attrs_to_ignore": ["/view", "/_no"],
    "color_code": "color_code"
}

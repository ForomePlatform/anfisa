#  Copyright (c) 2019. Partners HealthCare and other members of
#  Forome Association
#
#  Developed by Sergey Trifonov based on contributions by Joel Krier,
#  Michael Bouzinier, Shamil Sunyaev and other members of Division of
#  Genetics, Brigham and Women's Hospital
#
#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

from app.view.asp_set import AspectSetH
from app.view.aspect import AspectH
from app.view.attr import AttrH
from app.view.colgrp import ColGroupsH
from .favor import FavorSchema

#===============================================
def defineViewSchema(metadata_record = None):
    data_schema = (metadata_record.get("data_schema")
        if metadata_record else None)
    if data_schema == "FAVOR":
        return FavorSchema.defineViewSchema(metadata_record)
    assert data_schema is None or data_schema == "CASE", (
        "Bad data schema: " + data_schema)

    aspect_list = [
        AspectH("view_gen", "General", "_view", field = "general"),
        AspectH("view_transcripts", "Transcripts", "_view",
            col_groups = ColGroupsH(
                [("transcripts", "Transcripts")])),
        AspectH("view_qsamples", "Quality", "_view",
            col_groups = ColGroupsH(attr = "quality_samples")),
        AspectH("view_gnomAD", "gnomAD", "_view", field = "gnomAD"),
        AspectH("view_db", "Databases", "_view", field = "databases"),
        AspectH("view_pred", "Predictions", "_view", field = "predictions"),
        AspectH("view_pharmagkb", "Pharmacogenomics", "_view",
            field = "pharmacogenomics"),
        AspectH("view_genetics", "Bioinformatics", "_view",
            field = "bioinformatics")
    ]

    cohorts = metadata_record.get("cohorts") if metadata_record else None
    if cohorts:
        cohort_columns = [["ALL",  "ALL"]] + [
            [ch["name"],  ch.get("title",  ch["name"])] for ch in cohorts]
        aspect_list.append(AspectH("view_cohorts", "Cohorts", "_view",
            field = "cohorts",
            col_groups = ColGroupsH(attr_title_pairs = cohort_columns,
            single_columns = True)))

    aspect_list += [
        AspectH("view_inheritance", "Inheritance", "_view",
            field = "inheritance", ignored = True),
        AspectH("_main", "VEP Data", "__data"),
        AspectH("transcripts", "VEP Transcripts", "__data",
            col_groups = ColGroupsH([
                ("transcript_consequences", "Transcript"),
                ("regulatory_feature_consequences", "Regulatory"),
                ("motif_feature_consequences", "Motif"),
                ("intergenic_consequences", "Intergenic")])),
        AspectH("colocated_v", "Colocated Variants", "__data",
            col_groups = ColGroupsH(attr = "colocated_variants")),
        AspectH("input", "VCF", "__data", field = "input",
            mode = "string")]

    aspects = AspectSetH(aspect_list)

    aspects["view_gen"].setAttributes([
        AttrH("genes", title = "Gene(s)", is_seq = True,
            tooltip = "Gene Symbol (Ensembl classification)"),
        AttrH("hg19", tooltip = "Genetic coordinates in HG19 Assembly"),
        AttrH("hg38", tooltip = "Genetic coordinates in HG38 Assembly"),
        AttrH("worst_annotation", title = "Worst Annotation",
            tooltip = "Most Severe Consequences from the transcript"
            + " with the worst annotation"),
        AttrH("canonical_annotation", title = "Canonical Annotations",
            is_seq = True,
            tooltip = "Most Severe Consequences from canonical transcripts"),
        AttrH("refseq_transcript_canonical",
            title = "RefSeq Transcript (Canonical)", is_seq = True),
        AttrH("refseq_transcript_worst",
            title = "RefSeq Transcript (Worst)", is_seq = True),
        AttrH("ensembl_transcripts_canonical",
            title = "Ensembl Transcripts (Canonical)", is_seq = True),
        AttrH("ensembl_transcripts_worst",
            title = "Ensembl Transcripts (Worst)", is_seq = True),
        AttrH("ref", title = "Ref"),
        AttrH("alt", title = "Alt"),
        AttrH("mostly_expressed",
            title = "Mostly expressed in", is_seq = True),
        AttrH("splice_region", title = "Splice Region", is_seq = True),
        AttrH("gene_splicer", title = "GeneSplicer", is_seq = True),
        AttrH("splice_altering", title = "Splice AI splice altering"),
        AttrH("cpos_worst", title = "cPos (Worst)", is_seq = True),
        AttrH("cpos_canonical",
            title = "cPos (Canonical)", is_seq = True),
        AttrH("cpos_other", title = "cPos (Other)", is_seq = True),
        AttrH("ppos_worst", title = "pPos (Worst)", is_seq = True),
        AttrH("ppos_canonical",
            title = "pPos (Canonical)", is_seq = True),
        AttrH("ppos_other", title = "pPos (Other)", is_seq = True),
        AttrH("variant_exon_canonical",
            title = "Variant Exon (Canonical)", is_seq = True,
              tooltip = "Exon # according to canonical transcript"),
        AttrH("variant_exon_worst",
            title = "Variant Exon (Worst Annotation)", is_seq = True,
            tooltip = "Exon # according to the transcript with "
            "the worst annotation"),
        AttrH("variant_intron_worst",
            title = "Variant Intron (Worst Annotation)", is_seq = True,
            tooltip = "Intron # according to the transcript with "
            "the worst annotation"),
        AttrH("variant_intron_canonical",
            title = "Variant Intron (Canonical)", is_seq = True,
            tooltip = "Intron # according to canonical transcript"),
        AttrH("gene_panels", title = "Gene panels", is_seq = True),
        AttrH(None),
        AttrH("proband_genotype", title = "Proband Genotype"),
        AttrH("maternal_genotype", title = "Maternal Genotype"),
        AttrH("paternal_genotype", title = "Paternal Genotype"),
        AttrH("igv", title = "IGV", kind = "place",
            tooltip = "Open this variant in local IGV "
            "(https://software.broadinstitute.org/software/igv/)"),
        AttrH("ucsc", title = "View in UCSC", kind = "place",
            tooltip = "View this variant in UCSC Browser"),
        AttrH("transcripts",
            title = "Transcripts", is_seq = True),
        AttrH("op_filters", title = "Presence in filters", kind = "place",
            tooltip = "Filters positive on variant"),
        AttrH("op_dtrees", title = "Presence in decision trees",
            kind = "place", tooltip = "Decision trees positive on variant")
    ])

    aspects["view_transcripts"].setAttributes([
        AttrH("id", title = "Transcript Id"),
        AttrH("gene", title = "Gene"),
        AttrH("is_canonical", title = "Canonical"),
        AttrH("gencode_basic", title = "GENCODE Basic",
            tooltip =
            "The transcripts tagged as “basic” form part of a subset "
            "of representative transcripts for each gene. This subset "
            "prioritises full-length protein coding transcripts over "
            "partial or non-protein coding transcripts within the "
            "same gene, and intends to highlight those transcripts "
            "that will be useful to the majority of users."),
        AttrH("is_worst", title = "Worst?"),
        AttrH("transcript_source", title = "Source"),
        AttrH("biotype", title = "Biotype"),
        AttrH("transcript_annotations", title = "Consequences", is_seq = True),
        AttrH("variant_exon", title = "Exon"),
        AttrH("variant_intron", title = "Intron"),
        AttrH("tr_gene_panels", title = "Gene panels",
            is_seq = True, kind = "posted"),

        AttrH("cpos", title = "CPos"),
        AttrH("hgvs_c_snp_eff", title = "CPos SnpEff"),
        AttrH("hgvs_c_annovar", title = "CPos ANNOVAR"),
        AttrH("ppos", title = "PPos"),
        AttrH("hgvs_p_snp_eff", title = "PPos SnpEff"),
        AttrH("hgvs_p_annovar", title = "PPos ANNOVAR"),
        AttrH("amino_acids", title = "Amino acids"),

        AttrH("codons", title = "Codons"),
        AttrH("codonpos", title = "Codon Pos"),
        AttrH("refcodon", title = "Ref Codon"),
        AttrH("region", title="Gene Region"),
        AttrH("masked_region", title="Masked"),
        AttrH("dist_from_exon", title="Distance from Exon Boundary"),

        AttrH("polyphen2_hdiv_prediction", title = "Polyphen HDIV"),
        AttrH("polyphen2_hvar_prediction", title = "Polyphen HVAR"),
        AttrH("sift_prediction", title = "SIFT"),
        AttrH("sift_4g_prediction", title = "SIFT 4G"),
        AttrH("mutation_assessor_prediction", title = "Mutation Assessor"),
        AttrH("fathmm_prediction", title = "FATHMM"),

        AttrH("polyphen2_hdiv_score", title = "Polyphen HDIV Score"),
        AttrH("polyphen2_hvar_score", title = "Polyphen HVAR Score"),
        AttrH("sift_score", title = "SIFT Score"),
        AttrH("sift_4g_score", title = "SIFT 4G Score"),
        AttrH("mutation_assessor_score", title = "Mutation Assessor Score"),
        AttrH("fathmm_score", title = "FATHMM Score"),
        AttrH("mpc_score", title = "MPC Score"),

        AttrH("ensembl_gene_id", title = "Gene Id", kind = "hidden"),
        AttrH("ensembl_protein_id", title = "Protein Id", kind = "hidden"),
        AttrH("uniprot_acc", title = "Uniprot", kind = "place"),

    ])

    aspects["view_qsamples"].setAttributes([
        AttrH("title", title = "Title"),
        AttrH("qd", title = "Quality by Depth",
            tooltip = "The QUAL score normalized by allele depth (AD) "
            "for a variant. This annotation puts the variant confidence "
            "QUAL score into perspective by normalizing for the amount "
            "of coverage available. Because each read contributes a little "
            "to the QUAL score, variants in regions with deep coverage "
            "can have artificially inflated QUAL scores, giving the "
            "impression that the call is supported by more evidence "
            "than it really is. To compensate for this, we normalize "
            "the variant confidence by depth, which gives us a more "
            "objective picture of how well supported the call is."),
        AttrH("mq", title = "Mapping Quality",
            tooltip = "This is the root mean square mapping quality over all "
            "the reads at the site. Instead of the average mapping "
            "quality of the site, this annotation gives the square root "
            "of the average of the squares of the mapping qualities at "
            "the site. When the mapping qualities are good at a site, "
            "the MQ will be around 60. Broad Institute recommendation is "
            "to fail any variant with an MQ value less than 40.0"),
        AttrH("variant_call_quality", title = "Variant Call Quality",
            tooltip = "QUAL tells you how confident we are that there is "
            "some kind of variation at a given site. The variation may be "
            "present in one or more samples."),
        AttrH("strand_odds_ratio", title = "Strand Odds Ratio",
            tooltip = "Another way to estimate strand bias using a "
            "test similar to the symmetric odds ratio test. "
            "SOR was created because FS tends to penalize variants "
            "that occur at the ends of exons. Reads at the ends of "
            "exons tend to only be covered by reads in one direction "
            "and FS gives those variants a bad score. SOR will take "
            "into account the ratios of reads that cover both alleles."),
        AttrH("fs", title = "Fisher Strand Bias",
            tooltip = "Phred-scaled probability that there is strand bias at "
            "the site. Strand Bias tells us whether the alternate "
            "allele was seen more or less often on the forward or "
            "reverse strand than the reference allele. When there "
            "little to no strand bias at the site, the FS value "
            "will be close to 0."),
        AttrH("allelic_depth", title = "Allelic Depth", is_seq = True,
            tooltip = "AD is the unfiltered allele depth, i.e. "
            "the number of reads that support each of the reported "
            "alleles. All reads at the position (including reads that "
            "did not pass the variant caller's filters) are included in "
            "this number, except reads that were considered uninformative. "
            "Reads are considered uninformative when they do not provide "
            "enough statistical evidence to support one allele over another."),
        AttrH("read_depth", title = "Read Depth",
            tooltip = "DP - is a number of times that base pair locus "
            "was read"),
        AttrH("ft", title = "FILTERs",
            tooltip = "This field contains the name(s) of any filter(s) "
            "that the variant fails to pass, or the value PASS if the "
            "variant passed all filters. If the FILTER value is ., "
            "then no filtering has been applied to the records."),
        AttrH("genotype_quality", title = "Genotype Quality",
            tooltip = "GQ tells you how confident we are that "
            "the genotype we assigned to a particular sample is correct. "
            "It is simply the second lowest PL, because it is the "
            "difference between the second lowest PL and the lowest PL "
            "(always 0)."),
        AttrH("genotype", title = "Sample Genotype")
    ])

    aspects["view_gnomAD"].setAttributes([
        AttrH("allele", title = "Allele"),
        AttrH("proband", title = "Proband"),
        AttrH("pli", title = "pLI", is_seq = True),
        AttrH("af", title = "Overall AF"),
        AttrH("genome_af", title = "Genome AF"),
        AttrH("exome_af", title = "Exome AF"),
        AttrH("hom", title = "Number of homozygotes"),
        AttrH("hem", title = "Number of hemizygotes"),
        AttrH("genome_an", title = "Genome AN"),
        AttrH("exome_an", title = "Exome AN"),
        AttrH("url", title = "URL", kind = "link", is_seq = True),
        AttrH("popmax", title = "PopMax (outbred populations)", ),
        AttrH("raw_popmax", title = "PopMax (including inbred)",)
    ])

    aspects["view_db"].setAttributes([
        AttrH("hgmd", title = "HGMD"),
        AttrH("hgmd_hg38", title = "HGMD (HG38)"),
        AttrH("hgmd_tags", title = "HGMD TAGs", is_seq = True),
        AttrH("hgmd_phenotypes", title = "HGMD Phenotypes",
            is_seq = True),
        AttrH("hgmd_pmids", title = "HGMD PMIDs",
            is_seq = True, kind = "place"),
        AttrH("omim", title = "OMIM",
            is_seq = True, kind = "place"),
        AttrH("clinVar_variants", title = "ClinVar Variants",
            is_seq = True),
        AttrH("clinVar_significance", title = "ClinVar Significance",
            is_seq = True),
        AttrH("clinvar_review_status", title = "ClinVar Review Status",
            is_seq = False),
        AttrH("num_clinvar_submitters",
            title = "ClinVar: Number of submitters", is_seq = False),
        AttrH("clinvar_acmg_guidelines", title = "ClinVar ACMG Guidelines",
            is_seq = True),
        AttrH("lmm_significance", title = "Clinical Significance by LMM"),
        AttrH("gene_dx_significance",
            title = "Clinical Significance by GeneDx"),
        AttrH("clinVar_phenotypes", title = "ClinVar Phenotypes",
            is_seq = True),
        AttrH("clinVar_submitters", title = "ClinVar Submitters",
            is_seq = True),
        AttrH("clinVar", title = "ClinVar",
            is_seq = True, kind = "link"),
        AttrH("gtex", kind = "place",),
        AttrH("gene_cards", title = "GeneCards",
            is_seq = True, kind = "place"),
        AttrH("grev", is_seq = True, kind = "place"),
        AttrH("medgen", is_seq = True, kind = "place"),
        # AttrH("pubmed_search", title = "PubMed Search Results",
        #     is_seq = True, kind = "link"),
        AttrH("beacons", title = "Observed at", is_seq = True),
        AttrH("references", is_seq = True, kind = "place")])

    aspects["view_pred"].setAttributes([
        AttrH("lof_score", title = "LoF Score",
            is_seq = True),
        AttrH("lof_score_canonical", title = "LoF Score (Canonical)",
            is_seq = True),
        AttrH("max_ent_scan", title = "MaxEntScan",
            is_seq = True),
        AttrH("polyphen", title = "Polyphen",
            is_seq = True,
            tooltip =
            "https://brb.nci.nih.gov/seqtools/colexpanno.html#dbnsfp"),
        AttrH("polyphen2_hvar", title = "Polyphen 2 HVAR",
            is_seq = True,
            tooltip = "HumVar (HVAR) is PolyPhen-2 classifier "
            "trained on known human variation (disease mutations vs."
            " common neutral variants)"),
        AttrH("polyphen2_hdiv", title = "Polyphen 2 HDIV",
            is_seq = True,
            tooltip = "HumDiv (HDIV) classifier is trained on a smaller "
            "number of select extreme effect disease mutations vs. divergence "
            "with close homologs (e.g. primates), which is supposed to "
            "consist of mostly neutral mutations."),
        AttrH("sift", title = "SIFT from dbNSFP",
            is_seq = True,
            tooltip = "Sort intolerated from tolerated (An amino acid at a "
            "position is tolerated | The most frequentest amino acid "
            "being tolerated). D: Deleterious T: tolerated"),
        AttrH("sift_vep", title = "SIFT from VEP",
            is_seq = True),
        AttrH("revel", title = "REVEL",
            is_seq = True),
        AttrH("mutation_taster", title = "Mutation Taster",
            is_seq = True,
            tooltip = "Bayes Classifier. A: (disease_causing_automatic); "
            "D: (disease_causing); N: (polymorphism [probably harmless]); "
            "P: (polymorphism_automatic[known to be harmless])"),
        AttrH("mutation_assessor_predictions", title = "MutationAssessor",
            is_seq = True,
            tooltip = "MutationAssessor functional impact of a variant : "
            "predicted functional, i.e. high (“H”) or medium (“M”), "
            "or predicted non-functional, i.e. low (“L”) or neutral (“N”). "
            "The MAori score cutoffs between “H” and “M”, “M” and “L”, and "
            "“L” and “N”, are 3.5, 1.935 and 0.8, respectively. The "
            "rankscore cutoffs between “H” and “M”, “M” and “L”, and “L” "
            "and “L”, are 0.92922, 0.51944 and 0.19719, respectively."),
        AttrH("fathmm", title = "FATHMM", is_seq = True,
            tooltip = "Functional analysis through hidden markov model HMM."
            "D: Deleterious; T: Tolerated"),
        AttrH("primate_ai_pred", title = "PrimateAI", is_seq = True,
            tooltip = "Prediction of PrimateAI score based on the authors "
            "recommendation, “T(olerated)” or “D(amaging)”. "
            "The score cutoff between “D” and “T” is 0.803."),
        AttrH("cadd_phred", title = "CADD (Phred)",
            is_seq = True,
            tooltip = "CADD Combined annotation dependent depletion"),
        AttrH("cadd_raw", title = "CADD (Raw)",
            is_seq = True,
            tooltip = "CADD Combined annotation dependent depletion"),
        # AttrH("mutation_assessor", title = "Mutation Assessor",
        #     is_seq = True,
        #     tooltip = "Entropy of multiple sequence alighnment.	"
        #     "H: high; M: medium; L: low; N: neutral. H/M means functional "
        #     "and L/N means non-functional higher values "
        #     "are more deleterious"),
        AttrH("sift_score", title = "SIFT score",
            is_seq = True),
        AttrH("polyphen2_hvar_score", title = "Polyphen 2 HVAR score",
            is_seq = True),
        AttrH("polyphen2_hdiv_score", title = "Polyphen 2 HDIV score",
            is_seq = True),
        AttrH("mutation_assessor_scores",
            title = "MutationAssessor score (MAori)",
            tooltip = "MutationAssessor functional impact combined score "
            "(MAori). Multiple entries are separated by “;”, corresponding "
            "to Uniprot_entry.",
            is_seq = True),
        AttrH("dann_score", title = "DANN Functional Prediction score",
            tooltip = "DANN is a functional prediction score retrained based "
            "on the training data of CADD using deep neural network",
            is_seq = True)
    ])

    aspects["view_pharmagkb"].setAttributes([
        AttrH("diseases", title = "Diseases", is_seq = True, kind = "place"),
        AttrH("chemicals", title = "Chemicals", is_seq = True),
        AttrH("notes", title = "Notes", is_seq = True),
        AttrH("pmids", title = "PMIDs", is_seq = True)
        ])

    aspects["view_genetics"].setAttributes([
        AttrH("zygosity", title = "Zygosity"),
        AttrH("inherited_from", title = "Inherited from"),
        AttrH("region_worst",
            title = "Gene Region (Worst)",
            is_seq = True),
        AttrH("dist_from_exon_worst",
            title = "Distance From Intron/Exon Boundary (Worst)",
            is_seq = True),
        AttrH("region_canonical",
            title = "Gene Region (Canonical)",
            is_seq = True),
        AttrH("dist_from_exon_canonical",
            title = "Distance From Intron/Exon Boundary (Canonical)",
            is_seq = True),
        AttrH("masked_region", title="Masked"),
        AttrH("gerp_rs", title = "GERP Score", is_seq = False),
        AttrH("conservation", title = "Conservation", kind = "json"),
        AttrH("species_with_variant",
            title = "Species with variant"),
        AttrH("species_with_others",
            title = "Species with other variants"),
        AttrH("max_ent_scan", title = "MaxEntScan", is_seq = True),
        AttrH("nn_splice", title = "NNSplice"),
        AttrH("human_splicing_finder", title = "Human Splicing Finder"),
        #AttrH("splice_ai", title = "Splice AI Max Score"),
        AttrH("splice_ai_ag", title = "Splice AI acceptor gain",
            is_seq = True),
        AttrH("splice_ai_al", title = "Splice AI acceptor loss",
            is_seq = True),
        AttrH("splice_ai_dg", title = "Splice AI donor gain", is_seq = True),
        AttrH("splice_ai_dl", title = "Splice AI donor loss", is_seq = True),
        AttrH("splice_ai", kind = "hidden"),
        AttrH("eqtl_gene", title = "EQTL Gene", is_seq = True),
        AttrH("refcodon", title = "Ref Codon(s)", is_seq = True),
        AttrH("other_genes",
            title = "Gene symbols from other transcripts",
            is_seq = True),
        AttrH("called_by", title = "Called by", is_seq = True),
        AttrH("caller_data", title = "CALLER DATA")])

    if cohorts:
        aspects["view_cohorts"].setAttributes([
            AttrH("AF"),
            AttrH("AF2", title = "AF_Hom")])

    aspects["_main"].setAttributes([
        AttrH("label"),
        AttrH("color_code"),
        AttrH("id"),
        AttrH("assembly_name", title = "Assembly"),
        AttrH("seq_region_name"),
        AttrH("start"),
        AttrH("end"),
        AttrH("strand"),
        AttrH("allele_string"),
        AttrH("variant_class"),
        AttrH("most_severe_consequence"),
        AttrH("ClinVar"),
        AttrH("clinvar_variants", is_seq = True),
        AttrH("clinvar_phenotypes", is_seq = True),
        AttrH("clinvar_significance", is_seq = True),
        AttrH("HGMD"),
        AttrH("HGMD_HG38"),
        AttrH("HGMD_PIMIDs", kind = "hidden", is_seq = True),
        AttrH("HGMD_phenotypes", kind = "hidden", is_seq = True),
        AttrH("EXPECTED"),
        AttrH("gnomad_db_genomes_af", kind = "hidden"),
        AttrH("gnomad_db_exomes_af", kind = "hidden"),
        AttrH("SEQaBOO")])

    aspects["transcripts"].setAttributes([
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
        AttrH("domains", kind = "json"),
        AttrH("exacpli"),
        AttrH("exon"),
        AttrH("fathmm_pred"),
        AttrH("fathmm_score"),
        AttrH("flags", is_seq = True),
        AttrH("gene_id"),
        AttrH("gene_pheno"),
        AttrH("genesplicer"),
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
        AttrH("loftool"),
        AttrH("maxentscan_alt"),
        AttrH("maxentscan_diff"),
        AttrH("maxentscan_ref"),
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
        AttrH("spliceregion", is_seq = True),
        AttrH("swissprot", is_seq = True),
        AttrH("transcript_id"),
        AttrH("trembl", is_seq = True),
        AttrH("uniparc", is_seq = True),
        AttrH("used_ref"),
        AttrH("variant_allele")])

    aspects["colocated_v"].setAttributes([
        AttrH("id"),
        AttrH("start"),
        AttrH("end"),
        AttrH("allele_string"),
        AttrH("strand"),
        AttrH("pubmed", is_seq = True),
        AttrH("somatic"),
        AttrH("gnomAD"),
        AttrH("frequencies", kind = "json"),
        AttrH("phenotype_or_disease"),
        AttrH("seq_region_name"),
        AttrH("clin_sig", is_seq = True),
        AttrH("minor")])

    return aspects

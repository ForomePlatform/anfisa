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

from app.eval.var_reg import VarRegistry
#===============================================
anfisaVariables = VarRegistry()

anfisaVariables.setupClassificationFacet(1, "Knowledge Domain", [
    ["call", "Call Annotations"],
    ["phenotype", "Phenotypic Data"],
    ["rules", "Compound Rules"],
    ["popgen", "Population Genetics"],
    ["function", "Functional"],
    ["animal", "Animal Genetics"],
    ["human", "Human Genetics"],
    ["epigenetics", "Epigenetics"],
    ["na1", "N/A"]
])

anfisaVariables.setupClassificationFacet(2, "Scale", [
    ["transcript", "Transcript"],
    ["variant", "Variant"],
    ["position", "Position"],
    ["window", "Window"],
    ["gene", "Gene"],
    #["na2", "N/A"]
])

anfisaVariables.setupClassificationFacet(3, "Method", [
    ["statgen", "Statistical Genetics Evidence"],
    ["bioinf", "Bioinformatics Inference"],
    ["in-vivo", "Experimental, in Vivo"],
    ["in-vitro", "Experimental, in Vitro"],
    ["exp", "Experimental, Other"],
    ["clinical", "Clinical Evidence"],
    ["raw", "Raw Data"],
    ["na3", "N/A"]
])

anfisaVariables.regVar("Rules", "enum",
    facet1 = "rules")

#======================================
# viewGroup("Inheritance")
#======================================
anfisaVariables.predeclareClassification("phenotype", "variant", "na3")

anfisaVariables.regVar("Variant_in", "enum",
    title = "Variant presence in cohorts")

anfisaVariables.regVar("Callers", "enum",
    title = "Called by", facet1="call")

anfisaVariables.regVar("Inheritance_Mode", "func",
    title = "Inheritance Mode")

anfisaVariables.regVar("Custom_Inheritance_Mode", "func",
    title = "Custom Inheritance Mode")

anfisaVariables.regVar("Compound_Het", "func",
    title = "Calculated Compound", facet2="gene")  # Misha:check it

anfisaVariables.regVar("Compound_Request", "func",
    title = "Calculated Compound Request", facet2="gene")

anfisaVariables.regVar("Proband_Zygosity", "enum",
    title = "Proband Zygosity")

anfisaVariables.regVar("Num_Samples", "numeric",
    title = "Number of Samples",
    tooltip = "Number of samples for which this variant has been called")

anfisaVariables.regVar("Has_Variant", "enum")

#======================================
# viewGroup("Cohorts")
#======================================

anfisaVariables.regVar("ALL_AF", "numeric",
    title = "AD for all cohorts")

anfisaVariables.regVar("ALL_AF2", "numeric",
    title = "AF Hom for all cohorts")

anfisaVariables.regVarTemplate("numeric",
    prefix = "Cohort_", postfix = "_AF",
    title = "AF for cohort %s")

anfisaVariables.regVarTemplate("numeric",
    prefix = "Cohort_", postfix = "_AF2",
    title = "AF Hom for cohort %s")

#======================================
# viewGroup("Variant")
#======================================
anfisaVariables.predeclareClassification(
    "na1", "variant", "na3")

anfisaVariables.regVar("Variant_Class", "enum",
    tooltip = "Variant class as returned by VEP. "
    "The class of a variant is based on Sequence "
    "Ontology and is called according to its component "
    "alleles and its mapping to the reference genome. "
    "https://useast.ensembl.org/info/genome/variation/"
    "prediction/classification.html#classes",
    facet1="function", facet2="transcript", facet3="bioinf")

anfisaVariables.regVar("Most_Severe_Consequence", "enum",
    facet1="function", facet2="variant", facet3="bioinf")

anfisaVariables.regVar("Canonical_Annotation", "enum",
    facet1="function", facet2="variant", facet3="bioinf")

anfisaVariables.regVar("Multiallelic", "enum",
    title = "Multi-allelic?",
    facet1="call")

anfisaVariables.regVar("Altered_VCF", "enum",
    title = "Has VCF been normalized?", facet1="call")

anfisaVariables.regVar("Number_ALTs", "numeric",
    title = "Number of Alternative alleles", facet1="call")

# anfisaVariables.regVar("zyg_len", "numeric")

#======================================
# viewGroup("Genes")
#======================================
anfisaVariables.predeclareClassification(
    "na1", "transcript", "na3")

anfisaVariables.regVar("Symbol", "enum")

anfisaVariables.regVar("Panels", "enum")

anfisaVariables.regVar("EQTL_Gene", "enum",
    title = "EQTL Gene", facet1="epigenetics",
        facet2="window", facet3="statgen")

# anfisaVariables.regVar("Transcripts", "enum")

anfisaVariables.regVar("Num_Genes", "numeric",
    title = "Number of overlapping genes",
                       facet2="position")

anfisaVariables.regVar("Num_Transcripts", "numeric",
    title = "Number of transcripts at the position",
                       facet2="position")

#======================================
# viewGroup("Transcripts")
#======================================
anfisaVariables.predeclareClassification(
    "na1", "transcript", "na3")

anfisaVariables.regVar("Transcript_consequence", "enum",
                       facet1="function", facet3="bioinf")

anfisaVariables.regVar("Transcript_canonical", "enum")

anfisaVariables.regVar("Transcript_GENCODE_Basic", "enum")

anfisaVariables.regVar("Transcript_biotype", "enum",
                       facet1="function", facet3="bioinf")

anfisaVariables.regVar("Transcript_worst", "enum",
                       facet1="function", facet3="bioinf")

anfisaVariables.regVar("Transcript_id", "enum")

anfisaVariables.regVar("Transctript_Gene", "enum")

anfisaVariables.regVar("Transcript_Gene_Panels", "enum")

anfisaVariables.regVar("Transcript_source", "enum")

anfisaVariables.regVar("Transcript_codon_pos", "enum")

anfisaVariables.regVar("Transcript_region", "enum",
    title= "Gene Region",
                       facet1="function", facet2="window")

anfisaVariables.regVar("Transcript_CDS", "enum",
    title= "CDS?")

anfisaVariables.regVar("Transcript_masked", "enum",
    title= "Masked")

anfisaVariables.regVar("Transcript_dist_from_exon", "numeric",
    title = "Distance from Exon Boundary")

# anfisaVariables.regVar("Transcript_strand", "enum")

#======================================
# viewGroup("Transcript_Predictions")
#======================================
anfisaVariables.predeclareClassification(
    "na1", "transcript", "bioinf")

anfisaVariables.regVar("Transcript_PolypPhen_HDIV", "enum", facet1="popgen")
anfisaVariables.regVar("Transcript_PolyPhen_HVAR", "enum", facet1="popgen")
anfisaVariables.regVar("Transcript_SIFT", "enum", facet1="function")
anfisaVariables.regVar("Transcript_SIFT_4G", "enum", facet1="function")
anfisaVariables.regVar("Transcript_FATHMM", "enum", facet1="function")

#======================================
# viewGroup("Coordinates")
#======================================
anfisaVariables.predeclareClassification(
    "human", "position", "na3")

anfisaVariables.regVar("Chromosome", "enum")

anfisaVariables.regVar("GeneRegion", "func",
    title = "Gene Region")

anfisaVariables.regVar("Start_Pos", "numeric",
    title = "Start Position", render_mode = "neighborhood")

anfisaVariables.regVar("End_Pos", "numeric",
    title = "End Position", render_mode = "neighborhood")

anfisaVariables.regVar("Dist_from_Exon", "numeric",
    title = "Distance From Intron/Exon Boundary",
    render_mode = "log,<")

anfisaVariables.regVar("Dist_from_Exon_Canonical", "numeric",
    title = "Distance From Intron/Exon Boundary (Canonical)",
    render_mode = "log,<")

anfisaVariables.regVar("Dist_from_Exon_Worst", "numeric",
    title = "Distance From Intron/Exon Boundary (Worst)",
    render_mode = "log,<")

anfisaVariables.regVar("Region_Canonical", "enum",
    title = "Region (Canonical)")

anfisaVariables.regVar("Region_Worst", "enum",
    title = "Region (Worst)")

anfisaVariables.regVar("Region", "enum",
    title = "Region (Legacy)")

anfisaVariables.regVar("In_hg19", "enum")

#======================================
# viewGroup("gnomAD")
#======================================
anfisaVariables.predeclareClassification(
    "popgen", "variant", "exp")

anfisaVariables.regVar("gnomAD_AF", "numeric",
    render_mode = "log,<",
    title = "gnomAD Allele Frequency (family)",
    tooltip = "gnomAD Overall Allele Frequency")

anfisaVariables.regVar("gnomAD_AF_Exomes", "numeric",
    render_mode = "log,<",
    title = "gnomAD Exome Allele Frequency (family)")

anfisaVariables.regVar("gnomAD_AF_Genomes", "numeric",
    render_mode = "log,<",
    title = "gnomAD Genome Allele Frequency (family)")

anfisaVariables.regVar("gnomAD_AF_Proband", "numeric",
    render_mode = "log,<",
    title = "gnomAD Allele Frequency (proband)",
    tooltip = "gnomAD Overall Allele Frequency "
    "for the allele present in proband")

anfisaVariables.regVar("gnomAD_PopMax_AF", "numeric",
    render_mode = "log,<",
    title = "PopMax Allele Frequency",
    tooltip = "Maximum allele frequency across outbred populations")

anfisaVariables.regVar("gnomAD_PopMax", "enum",
    title = "PopMax Ancestry",
    tooltip = "Outbred population that has the maximum allele frequency")

anfisaVariables.regVar("gnomAD_PopMax_AN", "numeric",
    render_mode = "log,>",
    title = "Number of alleles in outbred PopMax Ancestry")

anfisaVariables.regVar("gnomAD_PopMax_AF_Inbred", "numeric",
    render_mode = "log,<",
    title = "PopMax Allele Frequency (including inbred)",
    tooltip = "Maximum allele frequency across all populations "
    "(including inbred)")

anfisaVariables.regVar("gnomAD_PopMax_Inbred", "enum",
    render_mode = "log,<",
    title = "PopMax Ancestry (including inbred)",
    tooltip = "Population, including inbred, that has the maximum "
    "allele frequency")

anfisaVariables.regVar("gnomAD_PopMax_AN_Inbred", "numeric",
    render_mode = "log,>",
    title = "Number of alleles in (inbred) PopMax Ancestry")

anfisaVariables.regVar("gnomAD_Hom", "numeric",
    render_mode = "log,>",
    title = "gnomAD: Number of homozygous")

anfisaVariables.regVar("gnomAD_Hem", "numeric",
    render_mode = "log,>",
    title = "gnomAD: Number of hemizygous")

#======================================
# viewGroup("Databases")
#======================================
anfisaVariables.predeclareClassification(
    "human", "variant", "na3")

anfisaVariables.regVar("Presence_in_Databases", "enum",
    title = "Presence in Databases")

anfisaVariables.regVar("ClinVar_Submitters", "enum",
    title = "ClinVar Submitters", facet3="clinical")

anfisaVariables.regVar("Number_submitters", "numeric",
    title = "Number of ClinVar Submitters", facet3="clinical")

anfisaVariables.regVar("PMIDs", "enum",
    title = "PMIDs")

anfisaVariables.regVar("Number_pmid", "numeric",
    title = "Number of PMIDs")

# anfisaVariables.regVar("beacons", "enum"
#     title = "Observed at")

#======================================
# viewGroup("Call_Quality")
#======================================
anfisaVariables.predeclareClassification(
    "call", "variant", "na3")

anfisaVariables.regVar("Proband_GQ", "numeric",
    render_mode = "linear,>",
    title = "Genotype Quality (GQ) for Proband",
    tooltip = "GQ tells you how confident we are that "
    "the genotype we assigned to a particular sample is correct. "
    "It is simply the second lowest PL, because it is the "
    "difference between the second lowest PL and the lowest PL "
    "(always 0).")

anfisaVariables.regVar("Min_GQ", "numeric",
    render_mode = "linear,>",
    title = "Minimum GQ for the family",
    tooltip = "GQ tells you how confident we are that "
    "the genotype we assigned to a particular sample is correct. "
    "It is simply the second lowest PL, because it is the "
    "difference between the second lowest PL and the lowest PL "
    "(always 0).")

anfisaVariables.regVar("Max_GQ", "numeric",
    render_mode = "linear,=",
    title = "The highest GQ",
    tooltip= "Max(GQ) for those samples that have the variant")

anfisaVariables.regVar("Num_NO_CALL", "numeric",
    render_mode = "linear,=",
    title = "Number of NO_CALL samples",
    tooltip= "Number of samples with NO_CALL in the current site")

anfisaVariables.regVar("QUAL", "numeric",
    title = "Variant Call Quality")

anfisaVariables.regVar("QD", "numeric",
    render_mode = "linear,>",
    title = "Quality by Depth",
    tooltip = "The QUAL score normalized by allele depth (AD) "
    "for a variant. This annotation puts the variant confidence "
    "QUAL score into perspective by normalizing for the amount "
    "of coverage available. Because each read contributes a little "
    "to the QUAL score, variants in regions with deep coverage "
    "can have artificially inflated QUAL scores, giving the "
    "impression that the call is supported by more evidence "
    "than it really is. To compensate for this, we normalize "
    "the variant confidence by depth, which gives us a more "
    "objective picture of how well supported the call is.")

anfisaVariables.regVar("FS", "numeric",
    render_mode = "linear,<",
    title = "Fisher Strand Bias",
    tooltip = "Phred-scaled probability that there is strand bias "
    "at the site. Strand Bias tells us whether the alternate "
    "allele was seen more or less often on the forward or "
    "reverse strand than the reference allele. When there "
    "little to no strand bias at the site, the FS value "
    "will be close to 0.")

anfisaVariables.regVar("FT", "enum",
    title = "FILTER",
    tooltip = "This field contains the name(s) of any filter(s) "
    "that the variant fails to pass, or the value PASS if the "
    "variant passed all filters. If the FILTER value is ., "
    "then no filtering has been applied to the records.")

#======================================
# viewGroup("Predictions")
#======================================
anfisaVariables.predeclareClassification(
    "human", "variant", "clinical")

anfisaVariables.regVar("HGMD_Benign", "enum",
    title = "Categorized Benign in HGMD")

anfisaVariables.regVar("HGMD_Tags", "enum")

anfisaVariables.regVar("Clinvar_Benign", "enum",
    title = "Categorized Benign in ClinVar by all submitters")

anfisaVariables.regVar("ClinVar_Significance", "enum",
    title = "Clinical Significance in ClinVar")

anfisaVariables.regVar("Clinvar_Trusted_Significance", "enum",
    title = "ClinVar significance by trusted submitters only",
    tooltip = "Clinical Significance by ClinVar trusted submitters only")

anfisaVariables.regVar("Clinvar_Trusted_Simplified", "enum",
    tooltip = "Simplified Clinical Significance by trusted submitters only")

anfisaVariables.regVar("Clinvar_stars", "enum",
    render_mode = "log,>",
    title = "ClinVar Stars")

anfisaVariables.regVar("Number_of_clinvar_submitters", "numeric",
    render_mode = "log,>",
    title = "ClinVar: Number of Submitters")

anfisaVariables.regVar("Clinvar_review_status", "enum",
    title = "ClinVar Review Status")

anfisaVariables.regVar("Clinvar_criteria_provided", "enum",
    title = "ClinVar Criteria")

anfisaVariables.regVar("Clinvar_conflicts", "enum",
    title = "ClinVar Conflicts")

anfisaVariables.regVar("Clinvar_acmg_guidelines", "enum")

anfisaVariables.regVarTemplate("enum", prefix = "ClinVar_Significance_",
    title = "Clinical Significance by %s")

# anfisaVariables.regVar("Clinvar_Trusted_Benign", "enum",
#     title = "Categorized Benign by Clinvar Trusted Submitters")

anfisaVariables.regVar("splice_altering", "enum",
    title = "Splice AI splice altering", facet3="bioinf")

anfisaVariables.regVar("splice_ai_dsmax", "numeric",
    title = "Splice AI splice altering score",
    render_mode = "linear,>", facet3="bioinf")

anfisaVariables.regVar("Polyphen_2_HVAR", "enum",
    title = "Polyphen",
    tooltip = "HumVar (HVAR) is PolyPhen-2 classifier trained on known human "
    "variation (disease mutations vs. common neutral variants)",
                       facet2="transcript", facet3="bioinf")

anfisaVariables.regVar("Polyphen_2_HDIV", "enum",
    title = "Polyphen HDIV (High sensitivity)",
    tooltip = "HumDiv (HDIV) classifier is trained on a smaller "
    "number of select extreme effect disease mutations vs. "
    "divergence with close homologs (e.g. primates), which is "
    "supposed to consist of mostly neutral mutations.",
                       facet2="transcript", facet3="bioinf")

anfisaVariables.regVar("SIFT", "enum",
    tooltip = "Sort intolerated from tolerated (An amino acid at a "
    "position is tolerated | The most frequentest amino acid "
    "being tolerated). D: Deleterious T: tolerated",
    facet1="function", facet2="transcript", facet3="bioinf")

anfisaVariables.regVar("FATHMM", "enum",
    tooltip = "Functional analysis through hidden markov model HMM."
    "D: Deleterious; T: Tolerated",
        facet1="function", facet2="transcript", facet3="bioinf")

anfisaVariables.regVar("PrimateAI", "enum",
    tooltip = "Prediction of PrimateAI score based on the authors "
    "recommendation, “T(olerated)” or “D(amaging)”. "
    "The score cutoff between “D” and “T” is 0.803.",
        facet1="animal", facet3="bioinf")

anfisaVariables.regVar("GERP_score", "numeric",
    title = "GERP Score",
    render_mode = "linear,>",
    facet1="animal", facet2="position", facet3="bioinf")

#======================================
# viewGroup("Pharmacogenomics")
#======================================
anfisaVariables.predeclareClassification(
    "human", "variant", "clinical")

anfisaVariables.regVar("Diseases", "enum")

anfisaVariables.regVar("Chemicals", "enum")


#======================================
# viewGroup("Expression")
#======================================
anfisaVariables.predeclareClassification(
    "epigenetics", "gene", "in-vivo")

anfisaVariables.regVar("Mostly_Expressed_in", "enum")

#======================================
# viewGroup("Debug_Info")
#======================================

anfisaVariables.regVar("Severity", "numeric")

#======================================
# FAVOR
#======================================
anfisaVariables.regVar("Position", "numeric",
    render_mode = "neighborhood")

anfisaVariables.regVar("gnomAD_Total_AF", "numeric",
    title = "gnomAD Allele Frequency",
    render_mode = "log,<")

anfisaVariables.regVar("GENCODE_Category", "enum")

anfisaVariables.regVar("GENCODE_Exonic_Category", "enum")

anfisaVariables.regVar("TOPMed_QC_Status", "enum")

anfisaVariables.regVar("TOPMed_Bravo_AF", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("ExAC03", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("Disruptive_Missense", "enum")

anfisaVariables.regVar("CAGE_Promoter", "enum")

anfisaVariables.regVar("CAGE_Enhancer", "enum")

anfisaVariables.regVar("Gene_Hancer", "enum")

anfisaVariables.regVar("Super_Enhancer", "enum")

anfisaVariables.regVar("bStatistics", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("Freq1000bp", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("Rare1000bp", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("PolyPhenCat", "enum")

anfisaVariables.regVar("SIFTcat", "enum",
    tooltip = "Sort intolerated from tolerated (An amino acid at a "
        "position is tolerated | The most frequentest amino acid "
        "being tolerated).")
anfisaVariables.regVar("GC", "numeric",
    render_mode = "linear,<")

anfisaVariables.regVar("CpG", "numeric",
    render_mode = "linear,<")

#======================================
def _fixVarName(var_name):
    if var_name == "hg19":
        return "In_hg19"
    if var_name.endswith("_AF") or var_name.endswith("_AF2"):
        return "Cohort_" + var_name
    if var_name.endswith("_Significance"):
        return "ClinVar_Significance_" + var_name[:-13]
    return None

anfisaVariables.setFixFunc(_fixVarName)

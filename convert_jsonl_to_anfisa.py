#!/usr/bin/env python3
"""
Convert JSONL format to Anfisa-compatible JSON.gz format

Usage:
    python convert_jsonl_to_anfisa.py <input_jsonl> <dataset_name> [anfisa_home] [config_name]
    
Args:
    input_jsonl: Path to input JSONL file
    dataset_name: Name for the output dataset
    anfisa_home: Path to Anfisa home directory (optional, defaults to parent of script directory)
    config_name: Name of Anfisa config file (optional, will auto-detect if not provided)
"""

import json
import gzip
import sys
import os
import re
import glob
from pathlib import Path

def get_variant_class(ref, alt):
    """
    Determine variant class from ref and alt alleles
    """
    if not ref or not alt:
        return "unknown"
    
    ref_len = len(ref)
    alt_len = len(alt)
    
    if ref_len == 1 and alt_len == 1:
        return "SNV"
    elif ref_len > alt_len:
        return "deletion"
    elif ref_len < alt_len:
        return "insertion"
    else:
        return "substitution"

def extract_ref_alt_from_hgvs(hgvs_c):
    """
    Extract ref and alt nucleotides from HGVS notation
    Examples: c.112A>G -> ('A', 'G')
              c.34_35del -> ('del', '')
              c.45insT -> ('', 'T')
    """
    if not hgvs_c:
        return None, None
    
    # Match substitution pattern like c.112A>G
    match = re.search(r'c\.\d+([ACGT])>([ACGT])', hgvs_c)
    if match:
        return match.group(1), match.group(2)
    
    # Match deletion pattern
    if 'del' in hgvs_c:
        return 'del', '-'
    
    # Match insertion pattern
    match = re.search(r'c\.\d+(?:_\d+)?ins([ACGT]+)', hgvs_c)
    if match:
        return '-', match.group(1)
    
    return None, None

def convert_jsonl_to_anfisa(input_file, output_file):
    """
    Convert JSONL file to Anfisa JSON.gz format
    
    Args:
        input_file: Path to input JSONL file
        output_file: Path to output JSON.gz file
    """
    records = []
    metadata_record = None
    sample_names = []
    
    # Read JSONL file
    print(f"Reading JSONL file: {input_file}")
    with open(input_file, 'r') as f:
        for line_num, line in enumerate(f, 1):
            if not line.strip():
                continue
            
            # Parse JSON directly from line
            try:
                json_data = json.loads(line.strip())
                
                # If this is metadata, extract sample names
                if json_data.get("record_type") == "metadata":
                    metadata_record = json_data
                    if "samples" in json_data:
                        sample_names = list(json_data["samples"].keys())
                
                # Convert to Anfisa format
                anfisa_record = convert_record_to_anfisa(json_data, line_num, sample_names)
                records.append(anfisa_record)
                
            except json.JSONDecodeError as e:
                print(f"Warning: JSON decode error on line {line_num}: {e}")
                continue
    
    print(f"Converted {len(records)} records")
    
    # Write to gzipped JSON file (one record per line, like the pgp3140 example)
    print(f"Writing Anfisa format to: {output_file}")
    with gzip.open(output_file, 'wt', encoding='utf-8') as f:
        for record in records:
            json.dump(record, f, ensure_ascii=False, separators=(',', ':'))
            f.write('\n')
    
    print("Conversion complete!")

def convert_record_to_anfisa(record, line_num, sample_names=None):
    """
    Convert a single record to Anfisa format
    
    The Anfisa format expects:
    - record_type: "metadata" or "variant"
    - _view: display information
    - _filters: filtering information
    - __data: raw data
    """
    
    # Check if this is a metadata record
    if record.get("record_type") == "metadata":
        # Fix data_schema if needed
        if "data_schema" in record and record["data_schema"] == "":
            record["data_schema"] = "CASE"
        
        # Add required fields if missing
        if "versions" not in record:
            record["versions"] = {
                "pipeline": "custom",
                "reference": "GRCh38",
                "annotations": "1.0"
            }
        
        # Fix modes field
        if "modes" not in record or not record["modes"]:
            record["modes"] = ["hg38"]
        
        return record
    
    # For variant records, we need to structure the data properly
    anfisa_record = {
        "record_type": "variant"
    }
    
    # Get genomic coordinates and alleles from the record
    chromosome = record.get("chromosome", "1")
    start = record.get("start", line_num * 1000)
    end = record.get("end", start)
    ref = record.get("ref", "N")
    alt = record.get("alt", "N")
    
    # Parse genes if it's a string
    genes_raw = record.get("genes", [])
    if isinstance(genes_raw, str):
        try:
            import ast
            genes = ast.literal_eval(genes_raw) if genes_raw else []
        except:
            genes = []
    else:
        genes = genes_raw
    
    # Create _view section (what's displayed in the UI)
    anfisa_record["_view"] = {
        "general": {
            "hg38": f"chr{chromosome}:{start} {ref}>{alt}",
            "hg19": f"chr{chromosome}:{start}-{end} {ref}>{alt}",
            "worst_annotation": "intergenic_variant",
            "canonical_annotation": ["intergenic_variant"],
            "variant_exon_canonical": [],
            "variant_intron_canonical": [],
            "genes": genes,
            "transcripts": [],
            "ppos_canonical": [],
            "ppos_worst": [],
            "cpos_canonical": [],
            "cpos_worst": [],
            "proband_genotype": "N/N",
            "maternal_genotype": "N/N",
            "paternal_genotype": "N/N",
            "mostly_expressed": []
        },
        "databases": {
            "references": []  # PubMed references
        },
        "quality_samples": [],  # Will be populated below
        "gnomAD": {},
        "predictions": {
            "polyphen2_hvar_score": [],
            "polyphen2_hdiv_score": [],
            "sift_score": [],
            "mutation_assessor_scores": [],
            "cadd_raw": [],
            "cadd_phred": [],
            "dann_score": [],
            "revel": [],
            "primate_ai_pred": []
        },
        "bioinformatics": {
            "zygosity": "Unknown",
            "inherited_from": None,
            "gerp_rs": None,
            "splice_ai": {},
            "eqtl_gene": [],
            "refcodon": [],
            "region_canonical": [],
            "region_worst": [],
            "masked_region": False,
            "species_with_variant": "",
            "species_with_others": "",
            "other_genes": [],
            "cnv_lo": None,
            "conservation": None
        },
        "pharmacogenomics": {
            "diseases": None,
            "chemicals": None,
            "pmids": None,
            "notes": None
        },
        "transcripts": [],  # Will be populated with proper format below
        "inheritance": {},
        "cohorts": None,
        "facets": []
    }
    
    # Map fields from your format to Anfisa format
    # ClinVar fields
    if "clinvar_significance" in record:
        anfisa_record["_view"]["databases"]["clinVar_significance"] = [record["clinvar_significance"]]
    if "clinvar_review_status" in record:
        anfisa_record["_view"]["databases"]["clinvar_review_status"] = record["clinvar_review_status"]
    if "clinvar_submitters" in record and record["clinvar_submitters"] is not None:
        anfisa_record["_view"]["databases"]["clinVar_submitters"] = [
            f"{sub['SubmitterName']}: {record.get('clinvar_significance', 'Unknown')}" 
            for sub in record["clinvar_submitters"]
        ]
    
    # gnomAD fields
    gnomad_data = {}
    if "gnomad_af" in record:
        gnomad_data["af"] = record["gnomad_af"]
    if "gnomad_af_genomes" in record:
        try:
            gnomad_data["genome_af"] = float(record["gnomad_af_genomes"]) if record["gnomad_af_genomes"] else None
        except (ValueError, TypeError):
            gnomad_data["genome_af"] = None
    if "gnomad_af_exomes" in record:
        try:
            gnomad_data["exome_af"] = float(record["gnomad_af_exomes"]) if record["gnomad_af_exomes"] else None
        except (ValueError, TypeError):
            gnomad_data["exome_af"] = None
    if "gnomad_hom" in record:
        gnomad_data["hom"] = record["gnomad_hom"]
    if "gnomad_hem" in record:
        gnomad_data["hem"] = record["gnomad_hem"]
    if "gnomad_popmax" in record:
        gnomad_data["popmax"] = record["gnomad_popmax"]
    if "gnomad_popmax_af" in record:
        gnomad_data["popmax_af"] = record["gnomad_popmax_af"]
    
    # Add required fields for gnomAD
    gnomad_data["url"] = [f"http://gnomad.broadinstitute.org/variant/{chromosome}-{start}-{ref}-{alt}"]
    gnomad_data["proband"] = "No"  # Placeholder
    gnomad_data["allele"] = alt
    
    anfisa_record["_view"]["gnomAD"] = gnomad_data
    
    # Create _filters section (used for filtering)
    anfisa_record["_filters"] = {
        "chromosome": f"chr{chromosome}",
        "start": start,
        "end": end,
        "ref": ref,
        "alt": alt,
        "filters": ["PASS"] if record.get("clinvar_benign") else [],
        "severity": 3 if record.get("clinvar_significance") == "Pathogenic" else (2 if record.get("clinvar_significance") == "Likely pathogenic" else 0),
        "region_canonical": [],
        "gnomad_af_pb": gnomad_data.get("af"),
        "gnomad_af_fam": gnomad_data.get("af"),
        "clinvar_benign": record.get("clinvar_benign", False),
        "clinvar_stars": 0 if not record.get("clinvar_stars") else int(record["clinvar_stars"].count("*")),
        "has_variant": []  # Will be populated below
    }
    
    # Zygosity
    if "zygosity" in record and record["zygosity"] is not None:
        zygosity_map = {0: "Homozygous Ref", 1: "Heterozygous", 2: "Homozygous Alt"}
        # Assuming zygosity array is [proband, mother, father]
        anfisa_record["_view"]["bioinformatics"]["zygosity"] = zygosity_map.get(record["zygosity"][0], "Unknown")
        
        # Update genotypes in general section
        if len(record["zygosity"]) >= 3:
            gt_map = {0: "N/N", 1: "N/X", 2: "X/X"}
            anfisa_record["_view"]["general"]["proband_genotype"] = gt_map.get(record["zygosity"][0], "N/N")
            anfisa_record["_view"]["general"]["maternal_genotype"] = gt_map.get(record["zygosity"][1], "N/N")
            anfisa_record["_view"]["general"]["paternal_genotype"] = gt_map.get(record["zygosity"][2], "N/N")
            
            # Calculate has_variant - samples with zygosity > 0 have the variant
            if sample_names and len(sample_names) == len(record["zygosity"]):
                has_variant_list = []
                for i, zyg_value in enumerate(record["zygosity"]):
                    if zyg_value > 0:  # 1 (het) or 2 (hom alt) means has variant
                        has_variant_list.append(sample_names[i])
                anfisa_record["_filters"]["has_variant"] = has_variant_list
    
    # Populate quality_samples based on available sample information
    quality_samples = [
        {
            "title": "All",
            "qd": 20.0,  # Placeholder quality values
            "mq": 60.0,
            "variant_call_quality": 1000.0,
            "strand_odds_ratio": 0.0,
            "fs": 0.0,
            "ft": ["PASS"]
        }
    ]
    
    # Add sample-specific quality data
    if sample_names:
        sample_titles = ["Proband", "Mother", "Father"]
        for i, sample_name in enumerate(sample_names[:3]):
            title = f"{sample_titles[i] if i < len(sample_titles) else 'Sample'}: {sample_name}"
            gt_map = {0: "HOM_REF:N*/N*", 1: "HET:N*/X", 2: "HOM_ALT:X/X"}
            zyg_value = record.get("zygosity", [0, 0, 0])[i] if "zygosity" in record and record["zygosity"] and i < len(record["zygosity"]) else 0
            
            quality_samples.append({
                "title": title,
                "read_depth": 30,  # Placeholder
                "allelic_depth": "N:30" if zyg_value == 0 else "N:15,X:15",
                "genotype_quality": 99,
                "genotype": gt_map.get(zyg_value, "HOM_REF:N*/N*")
            })
    
    anfisa_record["_view"]["quality_samples"] = quality_samples
    
    # Extract genes from transcripts if available and format transcripts
    if "transcripts" in record and record["transcripts"]:
        genes = []
        formatted_transcripts = []
        
        for i, transcript in enumerate(record["transcripts"]):
            if isinstance(transcript, dict):
                # Extract gene for general section
                gene = transcript.get("gene")
                if gene and gene not in genes:
                    genes.append(gene)
                
                # Format transcript for Anfisa
                formatted_transcript = {
                    "id": transcript.get("Ensembl_transcriptid", f"TR_{i}"),
                    "gene": gene or "Unknown",
                    "is_canonical": transcript.get("GENCODE_basic") == "Y",
                    "transcript_annotations": ["intergenic_variant"],  # Default
                    "region": "intergenic",  # Default
                    "biotype": "protein_coding",  # Default
                    "hgvs_c_snp_eff": transcript.get("HGVSc_snpEff"),
                    "hgvs_p_snp_eff": transcript.get("HGVSp_snpEff"),
                    "hgvs_c_annovar": transcript.get("HGVSc_ANNOVAR"),
                    "hgvs_p_annovar": transcript.get("HGVSp_ANNOVAR"),
                    "amino_acids": transcript.get("HGVSp_ANNOVAR", "").replace("p.", "") if transcript.get("HGVSp_ANNOVAR") else None,
                    "codons": transcript.get("refcodon"),
                    "polyphen2_hdiv_score": transcript.get("Polyphen2_HDIV_score"),
                    "polyphen2_hdiv_prediction": transcript.get("Polyphen2_HDIV_pred"),
                    "polyphen2_hvar_score": transcript.get("Polyphen2_HVAR_score"),
                    "polyphen2_hvar_prediction": transcript.get("Polyphen2_HVAR_pred"),
                    "sift_score": transcript.get("SIFT_score"),
                    "sift_prediction": transcript.get("SIFT_pred"),
                    "mutation_assessor_score": transcript.get("MutationAssessor_score"),
                    "mutation_assessor_prediction": transcript.get("MutationAssessor_pred"),
                    "fathmm_score": transcript.get("FATHMM_score"),
                    "fathmm_prediction": transcript.get("FATHMM_pred"),
                    "ensembl_gene_id": transcript.get("Ensembl_geneid"),
                    "ensembl_protein_id": transcript.get("Ensembl_proteinid"),
                    "uniprot_acc": transcript.get("Uniprot_acc")
                }
                formatted_transcripts.append(formatted_transcript)
        
        if genes:
            anfisa_record["_view"]["general"]["genes"] = genes
        
        if formatted_transcripts:
            anfisa_record["_view"]["transcripts"] = formatted_transcripts
    
    # Create __data section (raw data)
    anfisa_record["__data"] = {
        "input": f"chr{chromosome}\t{start}\t.\t{ref}\t{alt}\t.\tPASS\t.",
        "label": f"chr{chromosome}:{start} {ref}>{alt}",
        "seq_region_name": f"chr{chromosome}",
        "start": start,
        "end": end,
        "allele_string": "N/N",
        "variant_class": get_variant_class(ref, alt),
        "most_severe_consequence": "intergenic_variant",
        "assembly_name": "GRCh38",
        "strand": 1,
        "id": [f"var_{line_num}"],
        "region_canonical": ["intergenic"],
        "region_worst": ["intergenic"],
        "transcript_consequences": [],
        "regulatory_feature_consequences": [],
        "intergenic_consequences": [{
            "impact": "MODIFIER",
            "variant_allele": "N",
            "consequence_terms": ["intergenic_variant"]
        }],
        "colocated_variants": [],
        "hgmd_pmids": []  # Required field for HGMD PubMed IDs
    }
    
    # Add original data
    for key, value in record.items():
        if key not in anfisa_record["__data"]:
            anfisa_record["__data"][key] = value
    
    return anfisa_record

def create_config_file(dataset_name, input_file, output_dir):
    """
    Create a configuration file for the dataset
    """
    config = {
        "name": dataset_name,
        "case": dataset_name,
        "assembly": "GRCh38",
        "platform": "wgs",
        "config": os.path.join(output_dir, "config.json"),
        "a-json": os.path.join(output_dir, f"{dataset_name}_anfisa.json.gz"),
        "docs": []
    }
    
    config_file = os.path.join(output_dir, f"{dataset_name}.cfg")
    with open(config_file, 'w') as f:
        json.dump(config, f, indent=4)
    
    return config_file

def find_config_file(anfisa_repo):
    """
    Find Anfisa configuration file in the repository
    """
    # Look for .json config files in the anfisa directory
    config_files = glob.glob(os.path.join(anfisa_repo, '*.json'))
    
    # Filter out common non-config files
    config_files = [f for f in config_files if not any(exclude in os.path.basename(f).lower() 
                    for exclude in ['package', 'tsconfig', 'setup', 'manifest'])]
    
    if not config_files:
        return None
    elif len(config_files) == 1:
        return os.path.basename(config_files[0])
    else:
        # If multiple configs found, prefer one with 'anfisa' in the name
        anfisa_configs = [f for f in config_files if 'anfisa' in os.path.basename(f).lower()]
        if anfisa_configs:
            return os.path.basename(anfisa_configs[0])
        # Otherwise return the first one
        return os.path.basename(config_files[0])


def main():
    if len(sys.argv) < 2:
        print("Usage: python convert_jsonl_to_anfisa.py <input_jsonl_file> [dataset_name] [anfisa_home] [config_name]")
        print("\nExample:")
        print("  python convert_jsonl_to_anfisa.py input.jsonl my_dataset")
        print("  python convert_jsonl_to_anfisa.py input.jsonl my_dataset /path/to/anfisa-workspace")
        print("  python convert_jsonl_to_anfisa.py input.jsonl my_dataset /path/to/anfisa-workspace anfisa.json")
        sys.exit(1)
    
    input_file = sys.argv[1]
    
    if not os.path.exists(input_file):
        print(f"Error: Input file not found: {input_file}")
        sys.exit(1)
    
    # Get dataset name from argument or derive from filename
    if len(sys.argv) > 2:
        dataset_name = sys.argv[2]
    else:
        dataset_name = Path(input_file).stem
    
    # Get Anfisa home directory
    if len(sys.argv) > 3:
        anfisa_home = os.path.abspath(sys.argv[3])
    else:
        # Default: parent directory of the directory containing this script
        # e.g., if script is in /path/anfisa-workspace/anfisa/, home is /path/anfisa-workspace/
        script_dir = os.path.dirname(os.path.abspath(__file__))
        anfisa_home = os.path.dirname(script_dir)
    
    # Get config file name
    if len(sys.argv) > 4:
        config_name = sys.argv[4]
    else:
        config_name = None
    
    # Verify Anfisa home directory structure
    anfisa_repo = os.path.join(anfisa_home, 'anfisa')
    if not os.path.exists(anfisa_repo):
        print(f"Error: Anfisa repository not found at {anfisa_repo}")
        print(f"Please ensure {anfisa_home} contains the 'anfisa' repository directory")
        sys.exit(1)
    
    # Find or verify config file
    if not config_name:
        config_name = find_config_file(anfisa_repo)
        if not config_name:
            print(f"Error: No Anfisa configuration file found in {anfisa_repo}")
            print("Please specify the config file name as the 4th argument")
            sys.exit(1)
        print(f"Auto-detected config file: {config_name}")
    else:
        # Verify the specified config exists
        if not os.path.exists(os.path.join(anfisa_repo, config_name)):
            print(f"Error: Config file '{config_name}' not found in {anfisa_repo}")
            sys.exit(1)
    
    # Create output directory in anfisa repo
    output_dir = os.path.join(anfisa_repo, 'data', dataset_name)
    os.makedirs(output_dir, exist_ok=True)
    
    # Convert JSONL to Anfisa format
    output_file = os.path.join(output_dir, f"{dataset_name}_anfisa.json.gz")
    
    print(f"\nAnfisa home directory: {anfisa_home}")
    print(f"Anfisa repository: {anfisa_repo}")
    print(f"Output directory: {output_dir}\n")
    
    convert_jsonl_to_anfisa(input_file, output_file)
    
    # Create config file
    config_file = create_config_file(dataset_name, input_file, output_dir)
    
    print(f"\nConversion complete!")
    print(f"Output file: {output_file}")
    print(f"Config file: {config_file}")
    print(f"\nTo load the dataset into Anfisa, run:")
    print(f"cd {anfisa_repo}")
    print(f"python -m app.storage -c {config_name} -m create -f -k ws -i {config_file} {dataset_name}")

if __name__ == "__main__":
    main()

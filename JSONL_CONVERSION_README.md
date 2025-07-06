# JSONL to Anfisa Conversion Guide

This guide explains how to convert JSONL files to Anfisa format and load them into the Anfisa system.

## Prerequisites

1. Anfisa server installed and configured
2. Python 3.x
3. Input data in JSONL format with proper structure

## Script Usage

The conversion script `convert_jsonl_to_anfisa.py` is located in the Anfisa repository.

### Basic Usage

```bash
python convert_jsonl_to_anfisa.py <input_jsonl> <dataset_name> [anfisa_home] [config_name]
```

### Arguments

- `input_jsonl`: Path to your input JSONL file
- `dataset_name`: Name for your dataset (will be used in Anfisa)
- `anfisa_home`: (Optional) Path to Anfisa home directory. If not provided, defaults to the parent directory of where the script is located.
- `config_name`: (Optional) Name of Anfisa config file. If not provided, the script will auto-detect it.

### Examples

1. **Using all defaults** (auto-detect Anfisa home and config):
   ```bash
   python convert_jsonl_to_anfisa.py input.jsonl my_dataset
   ```

2. **Specifying custom Anfisa home**:
   ```bash
   python convert_jsonl_to_anfisa.py /path/to/data.jsonl my_dataset /path/to/anfisa-workspace
   ```

3. **Specifying both Anfisa home and config file**:
   ```bash
   python convert_jsonl_to_anfisa.py input.jsonl my_dataset /path/to/anfisa-workspace anfisa.json
   ```

4. **Real example with auto-detection**:
   ```bash
   cd /path/to/your/data
   python3 /path/to/anfisa/convert_jsonl_to_anfisa.py input.jsonl test_dataset
   ```

## Complete Workflow

### Step 1: Start Anfisa Server

```bash
cd /path/to/anfisa-workspace/anfisa
python -m app.run [config_file.json]
```

Note: The config file name (e.g., `anfisa.json`, `anfisa_local.json`) depends on your installation.

### Step 2: Convert JSONL to Anfisa Format

```bash
python convert_jsonl_to_anfisa.py input.jsonl my_dataset [anfisa_home]
```

This will:
- Create a data directory: `anfisa/data/my_dataset/`
- Generate compressed data file: `my_dataset_anfisa.json.gz`
- Create configuration file: `my_dataset.cfg`

### Step 3: Load Dataset into Anfisa

The script will output the exact command to run. It will look like:

```bash
cd /path/to/anfisa-workspace/anfisa
python -m app.storage -c [config_file.json] -m create -f -k ws -i data/my_dataset/my_dataset.cfg my_dataset
```

Options:
- `-m create`: Create new dataset
- `-f`: Force overwrite if exists
- `-k ws`: Create workspace type dataset
- `-i`: Path to configuration file

### Step 4: Access in Browser

Open your browser and navigate to:
```
http://localhost:8190
```

Your dataset will appear in the list. Click to open and explore.

## Expected JSONL Structure

The input JSONL file should have:

1. **First line**: Metadata record with `"record_type": "metadata"` containing:
   - `data_schema`: Should be "CASE" for case/trio analysis
   - `samples`: Sample information with family relationships
   - `versions`: Pipeline and tool versions

2. **Subsequent lines**: Variant records containing:
   - `chromosome`, `start`, `end`, `ref`, `alt`: Genomic coordinates
   - `zygosity`: Array of zygosity values for samples
   - `transcripts`: Array of transcript annotations (optional)
   - Clinical and frequency annotations

## Configuration Auto-Detection

The script can automatically detect your Anfisa configuration file. It:
1. Searches for `.json` files in the Anfisa repository directory
2. Filters out common non-config files (package.json, tsconfig.json, etc.)
3. Prefers files with 'anfisa' in the name if multiple configs exist
4. Shows which config file was auto-detected in the output

If auto-detection fails or selects the wrong file, you can specify the config file explicitly as the 4th argument.

## Troubleshooting

1. **"Anfisa repository not found" error**: 
   - Ensure the anfisa_home path contains the 'anfisa' subdirectory
   - The structure should be: `anfisa_home/anfisa/`

2. **"No Anfisa configuration file found" error**:
   - The auto-detection couldn't find a suitable config file
   - Specify the config file name explicitly as the 4th argument
   - Example: `python convert_jsonl_to_anfisa.py input.jsonl dataset /path/to/home anfisa.json`

3. **Dataset doesn't appear in UI**:
   - Check that Anfisa server is running
   - Verify the dataset was created without errors
   - Check the vault directory: `anfisa/vault/your_dataset_name/`

4. **Variants show incorrect information**:
   - Ensure your JSONL has proper genomic coordinates
   - Check that ref/alt alleles are in the correct format
   - Verify zygosity array matches the number of samples

## Output Files

After conversion, you'll find:
- `anfisa/data/[dataset_name]/[dataset_name]_anfisa.json.gz` - Compressed variant data
- `anfisa/data/[dataset_name]/[dataset_name].cfg` - Dataset configuration
- `anfisa/vault/[dataset_name]/` - Dataset workspace (after loading)

#!/bin/bash
#SBATCH --job-name=split_rna_rna3db_filtered    # Job name
#SBATCH --ntasks=1                # Run on a single CPU
#SBATCH --cpus-per-task=16
#SBATCH --mem=96gb                # Job memory request

#SBATCH --qos=yanjun.li-b
#SBATCH --time=1:00:00           # Time limit hrs:min:sec
#SBATCH --output=split_core.log       # Standard output and error log

# Print current working directory, hostname, and date
pwd; hostname; date

# Load conda environment
module load conda
conda activate hariboss

# Directories
PDB_DIR="../hariboss_process/complex_mmcif_database_non_rnasm_removed_rrna_removed"
OUTPUT_DIR="./output_core"
INDEX_DATA="../hariboss_process/hariboss_clean_20240621_error_revised_non_rnasm_removed_rrna_removed.csv"

# # Create output directory if it doesn't exist
# mkdir -p ${OUTPUT_DIR}/cmscans

# Step 1: Extracting RNAs from PDB
python -m rna3db parse ${PDB_DIR}/ ${OUTPUT_DIR}/parse.json
echo "$(date): RNA extraction from PDB finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# Step 2: Filter RNA IDs
python filter_rna.py ${OUTPUT_DIR}/parse.json ${INDEX_DATA} ${OUTPUT_DIR}/filtered_parse.json
echo "$(date): RNA filtering finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# # Step 3: Generate a FASTA file containing the RNAs we want to scan
# python rna3db/scripts/json_to_fasta.py ${OUTPUT_DIR}/filtered_parse.json ${OUTPUT_DIR}/filtered_parse.fasta
# echo "$(date): FASTA file generation finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# # Step 4: Run CMSCAN
# cmscan -o ${OUTPUT_DIR}/cmscans/parse.o --tbl ${OUTPUT_DIR}/cmscans/parse.tbl data/Rfam.cm ${OUTPUT_DIR}/filtered_parse.fasta
# echo "$(date): First CMSCAN run finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# # Step 5: Generate a FASTA of chains without hits in parse.tbl
# python rna3db/scripts/get_nohits.py ${OUTPUT_DIR}/filtered_parse.fasta ${OUTPUT_DIR}/nohits.fasta ${OUTPUT_DIR}/cmscans
# echo "$(date): FASTA of chains without hits generation finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# # Step 6: Run CMSCAN again with the --max flag
# cmscan --max -o ${OUTPUT_DIR}/cmscans/nohits.o --tbl ${OUTPUT_DIR}/cmscans/nohits.tbl data/Rfam.cm ${OUTPUT_DIR}/nohits.fasta
# echo "$(date): Second CMSCAN run finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# Step 7: Clustering
python -m rna3db cluster ${OUTPUT_DIR}/filtered_parse.json ${OUTPUT_DIR}/cluster.json --tbl_dir ${OUTPUT_DIR}/cmscans/
# python -m rna3db cluster ${OUTPUT_DIR}/filtered_parse.json ${OUTPUT_DIR}/cluster_ev5.json --tbl_dir ${OUTPUT_DIR}/cmscans/ --structural_e_value_cutoff 5.0 
echo "$(date): Clustering finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# Step 8: Clustering with only_sequence
python -m rna3db cluster ${OUTPUT_DIR}/filtered_parse.json ${OUTPUT_DIR}/cluster_seq.json --tbl_dir ${OUTPUT_DIR}/cmscans/ --only_sequence --min_seq_id 0.3
echo "$(date): Clustering with only_sequence finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

Step 9: Splitting clusters
# python -m rna3db split ${OUTPUT_DIR}/cluster_ev5.json ${OUTPUT_DIR}/split_ev5.json
python -m rna3db split ${OUTPUT_DIR}/cluster.json ${OUTPUT_DIR}/split.json

echo "$(date): Splitting cluster finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

python -m rna3db split ${OUTPUT_DIR}/cluster_seq.json ${OUTPUT_DIR}/split_seq.json
echo "$(date): Splitting cluster with only_sequence finished" >> ${OUTPUT_DIR}/split_rna_rna3db.log

# Print the completion date
date
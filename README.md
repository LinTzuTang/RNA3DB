# RNA3DB

A dataset of non-redundant RNA structures from the PDB. RNA3DB contains:

All RNA chains in the PDB, labelled with non-coding RNA families
Non-redundant clustering of the above chains, suitable for training and benchmarking deep learning models



### 0. see original rna3db

Pipeline overview:  
Step 1: Extracting RNAs from PDB  
Step 2: Filter RNA IDs  
Step 3: Generate a FASTA file containing the RNAs we want to scan  
Step 4: Run CMSCAN  
Step 5: Generate a FASTA of chains without hits in parse.tbl  
Step 6: Run CMSCAN again with the --max flag  
Step 7: Clustering  
Step 8: Clustering with only_sequence  
Step 9: Splitting clusters  

### 1. run RNA3DB
split_rna_rna3db_core.sh

### 2. split
rna3db_split.py

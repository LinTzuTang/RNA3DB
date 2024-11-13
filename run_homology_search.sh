#!/bin/bash
#SBATCH --job-name=homology_search    # Job name
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --cpus-per-task=128
#SBATCH --mem=96gb                   # Job memory request
#SBATCH --partition=bigmem
#SBATCH --time=96:00:00             # Time limit hrs:min:sec
#SBATCH --output=homology_search.log   # Standard output and error log
pwd; hostname; date

module load conda
conda activate hariboss

cmscan -o output/cmscans/parse.o --tbl output/cmscans/parse.tbl data/Rfam.cm output/parse.fasta

date

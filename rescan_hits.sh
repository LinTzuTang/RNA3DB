#!/bin/bash
#SBATCH --job-name=rescan_hits    # Job name
#SBATCH --ntasks=1                    # Run on a single CPU
#SBATCH --cpus-per-task=64
#SBATCH --mem=96gb                   # Job memory request
#SBATCH --partition=bigmem
#SBATCH --time=96:00:00             # Time limit hrs:min:sec
#SBATCH --output=rescan.log   # Standard output and error log
pwd; hostname; date

module load conda
conda activate hariboss

#python rna3db/scripts/get_nohits.py output/parse.fasta output/nohits.fasta output/cmscans
cmscan --max -o output/cmscans/nohits.o --tbl output/cmscans/nohits.tbl data/Rfam.cm output/nohits.fasta

date

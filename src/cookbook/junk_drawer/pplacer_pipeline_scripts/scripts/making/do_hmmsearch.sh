#!/bin/sh
# Submit via qsub

#PBS -d .
#PBS -N recruit

# Robin: This will run on nodes*ppn cores. Adjust as you like.
#PBS -l nodes=16:ppn=8,walltime=20:00:00

# Set database, directory containing HMMs
SEED_HMMDIR="/home/rkodner/prep/noodle/seed_alignments/PTZ_Clusters.aln/hmm/"
#REF_DB_PATH="/home/rkodner/refs/custom_refs/all_custom_refs_112911.dedup.fasta"
REF_DB_PATH=`pwd`/test.fasta

# Robin - you can adjust the e-value threshold here, as well as the tree building method
kaboodle-search-recruit $REF_DB_PATH $(find $SEED_HMMDIR -name "*.hmm") -E 1e-5 --tree-method=fasttree

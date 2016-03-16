#!/bin/sh
# Submit via qsub

#$ -S /bin/sh
#$ -cwd
#$ -N hmm-recruit
#$ -pe mpi 24
##$ -q all.q@compute-0-10.local
#$ -o "/home/mclaugr4/home2/refpkg_project_071414/makerefs/"
#$ -e "/home/mclaugr4/home2/refpkg_project_071414/makerefs/"

SEED_HMMDIR="/home/mclaugr4/home2/refpkg_project_071414/seed_alignments/KOG/"
REF_DB_PATH="/home/mclaugr4/home2/refpkg_project_071414/refseq/only_euks/refseq_MMETSP_only_euks.fasta"

export PATH=/home/mclaugr4/bio/wwubio/bin:$PATH

kaboodle-search-recruit $REF_DB_PATH $(find $SEED_HMMDIR -name "*.hmm") -E 1e-5 --tree-method=fasttree

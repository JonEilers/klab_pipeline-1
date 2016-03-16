#!/bin/sh
# Submit via qsub

#$ -S /bin/sh
#$ -cwd
#$ -N recruit-nest
#$ -pe mpi 24
##$ -q all.q@compute-0-0.local
#$ -o "/home/mclaugr4/home2/refpkg_project_071414/makerefs/"
#$ -e "/home/mclaugr4/home2/refpkg_project_071414/makerefs/"

REF_DB_PATH="/home/mclaugr4/home2/refpkg_project_071414/refseq/only_euks/refseq_MMETSP_only_euks.fasta"
export PATH=/home/mclaugr4/bio/wwubio/bin:$PATH

kaboodle-recruit-nest $REF_DB_PATH recruit/refseq_MMETSP_only_euks.domtblout recruit/hmm_map.json

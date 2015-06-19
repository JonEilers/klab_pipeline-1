#!/bin/sh
# Submit via qsub

#PBS -d .
#PBS -N recruit-nest

# Robin: This will run on nodes*ppn cores. Adjust as you like.
#PBS -l nodes=1:IB:ppn=1,walltime=20:00:00,pmem=8GB

# Set database, directory containing HMMs
REF_DB_PATH="/home/rkodner/refs/custom_refs/all_custom_refs_112911.dedup.fasta"

kaboodle-recruit-nest $REF_DB_PATH recruit/all_custom_refs_112911.domtbl.txt recruit/hmm_map.json

#!/bin/sh
# Submit via qsub

#PBS -d .
#PBS -N analysis

# Robin: This will run on nodes*ppn cores. Adjust as you like.
#PBS -l nodes=16:ppn=8,walltime=20:00:00

if [ -z "${PBS_O_PATH}" ]; then
  echo "Not running on PBS. Submit via qsub. Exiting"
  exit 1
fi

# Set database, directory containing HMMs
REFPKG_DIR="/home/mclaugr4/bio/scripts_built/pplacer_pipeline_scripts/refpkgs/clusters/"
META_DB_PATH="/home/mclaugr4/bio/scripts_built/pplacer_pipeline_scripts/metas/DCM_all_CDL_orfs.fasta"
#REF_DB_PATH=`pwd`/test.fasta

# Robin - you can adjust the e-value threshold here, as well as the tree building method
kaboodle-search-analysis $META_DB_PATH $REFPKG_DIR  -f

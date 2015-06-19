#!/bin/bash 

TEMPLPATH=/home/mclaugr4/bio/scripts_built/pplacer_pipeline_scripts/scripts/corral/00makeref.sh
TEMPLNAME=$(basename $TEMPLPATH)

nestrun \
   -j 2 \
   --template-file=$TEMPLPATH \
   --template="qsub $TEMPLNAME" \
   $(find runs -name control.json)

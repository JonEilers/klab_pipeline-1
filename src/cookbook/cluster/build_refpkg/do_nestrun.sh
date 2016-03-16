#!/bin/bash 

TEMPLPATH=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/scripts/corral/makeref.sh
TEMPLNAME=$(basename $TEMPLPATH)

nestrun \
   -j 2 \
   --template-file=$TEMPLPATH \
   --template="qsub $TEMPLNAME" \
   $(find runs -name control.json)

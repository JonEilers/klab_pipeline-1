#!/bin/bash 

TEMPLPATH=/home/mclaugr4/bio/scripts_built/pplacer_pipeline_scripts/scripts/corral/01search_place.sh
TEMPLNAME=$(basename $TEMPLPATH)

nestrun \
   -j 2 \
   --template-file=$TEMPLPATH \
   --template="qsub $TEMPLNAME" \
   $(find analysis -name control.json)

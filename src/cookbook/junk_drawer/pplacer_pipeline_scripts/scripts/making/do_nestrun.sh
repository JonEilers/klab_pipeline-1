#!/bin/bash 

TEMPLPATH=/home/rkodner/prep/kaboodle/scripts/corral/00makeref.sh
TEMPLNAME=$(basename $TEMPLPATH)

nestrun \
   -j 2 \
   --template-file=$TEMPLPATH \
   --template="qsub $TEMPLNAME" \
   $(find analysis -name control.json)

#!/bin/sh
# PYTHONPATH should be set to something like this in each user's .bashrc file
#PYTHONPATH=/share/research-groups/kodner/klab_pipeline/src

if [ -z "$PYTHONPATH" ]; then
    echo "Need to set PYTHONPATH"
    exit 1
fi  

python $PYTHONPATH/klab/analysis/diversity.py -d $1 -o $2

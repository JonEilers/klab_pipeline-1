#!/bin/sh

# Run 01search_place on all control files under analysis/
nestrun \
    --template 'qsub 01search_place.sh' \
    --no-log \
    --template-file $HOME/prep/kaboodle/scripts/corral/01search_place.sh \
    analysis/*/control.json

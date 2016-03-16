#!/bin/sh

REFPKG={refpkg}
REFPKG_BASE=$(basename $REFPKG .refpkg)
RECRUIT_PREFIX={title}.aligned

python /share/research-groups/kodner/cluster_pipeline/analyze_meta/refpkg_align.py align $REFPKG recruit.fasta $RECRUIT_PREFIX.sto
seqmagick convert --prune-empty $RECRUIT_PREFIX.sto $RECRUIT_PREFIX.fasta
rm -f $RECRUIT_PREFIX.unmasked.sto

pplacer -p -c $REFPKG $RECRUIT_PREFIX.fasta

# Generate a taxtable
rppr prep_db -c $REFPKG --sqlite taxtable.db

# Classify
guppy classify -c $REFPKG --sqlite taxtable.db $RECRUIT_PREFIX.jplace
guppy classify -c $REFPKG $RECRUIT_PREFIX.jplace

# Make a fat tree
guppy fat -c $REFPKG $RECRUIT_PREFIX.jplace

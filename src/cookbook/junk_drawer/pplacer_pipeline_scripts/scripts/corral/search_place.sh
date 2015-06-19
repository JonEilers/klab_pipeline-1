#!/bin/bash

#$ -S /bin/bash
#$ -cwd
#$ -N {title}
#$ -e search_place.err
##$ -o search_place.out


REFPKG={refpkg}
REFPKG_BASE=$(basename $REFPKG .refpkg)
RECRUIT_PREFIX={title}.aligned

python2.7 /home/mclaugr4/software/bin/refpkg_align.py align $REFPKG recruit.fasta $RECRUIT_PREFIX.sto
/home/mclaugr4/software/bin/seqmagick convert --prune-empty $RECRUIT_PREFIX.sto $RECRUIT_PREFIX.fasta
rm -f $RECRUIT_PREFIX.unmasked.sto

pplacer -p -c $REFPKG $RECRUIT_PREFIX.fasta

# Generate a taxtable
rppr prep_db -c $REFPKG --sqlite taxtable.db

# Classify
guppy classify -c $REFPKG --sqlite taxtable.db $RECRUIT_PREFIX.jplace
guppy classify -c $REFPKG $RECRUIT_PREFIX.jplace

# Make a fat tree
guppy fat -c $REFPKG $RECRUIT_PREFIX.jplace

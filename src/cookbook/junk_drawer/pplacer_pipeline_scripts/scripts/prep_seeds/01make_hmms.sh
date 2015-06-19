#! /bin/bash

WD=$(pwd)

for STO in sto/*; do
  BASE=$(basename $STO .sto)
  echo "hmmbuild $WD/hmm/$BASE.hmm $WD/$STO" | qsub -o oe_hmmbuild/$BASE.out -e oe_hmmbuild/$BASE.err -N $BASE
done

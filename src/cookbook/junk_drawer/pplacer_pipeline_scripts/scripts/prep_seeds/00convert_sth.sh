#! /bin/bash

for i in fasta/*; do
  echo $i
  seqmagick.py convert $i sto/$(basename $i .fasta).sto
done

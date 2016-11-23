#!/bin/sh

# This creates a conda environment for biological data science (bds). Note that it can create python 2.7x or
# python 3.5x environments. The default is python 2.7x

conda create -y -n bds anaconda biopython scikit-bio seaborn python=2
source activate bds

# TODO ech 2016-11-22 - write switch code for p3.5

pip install simplejson pytest jupyter seqmagick

# hmmer, infernal, mothur, pplacer, phylosift?

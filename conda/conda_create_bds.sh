#!/bin/sh

# This creates a conda environment for biological data science (bds). Note that it can create python 2.7x or
# python 3.5x environments. The default is python 2.7x

conda create -y -n bds biopython scikit-bio seaborn python
source activate bds

# TODO ech 2016-11-22 - write switch code for p3.5
#conda create -y -n bds3 anaconda biopython scikit-bio seaborn python=3

pip install simplejson jupyter seqmagick pytest coverage mock

# hmmer, infernal, mothur, pplacer, phylosift?

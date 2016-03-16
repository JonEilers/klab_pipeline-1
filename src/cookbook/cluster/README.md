# cluster_pipeline

This repo contains all the scripts required to do a basic analysis of a metagenome using the pplacer suit of scrips.

Below is a quick description of each dir:

./kaboodle-0.1.0-py2.7.egg
This is a python egg that contains the supporting scripts for the control scripts in both analyze_meta and build_refpkg.
WARNING: this must be installed for the pipeline to function.

./analyze_meta
This dir contains what you need to run a metagenome on an existing set of refpkgs.
Look inside for the README of how to do that.

./archive_pplacer_pipline_scripts
This dir contains all original scripts brought by Robin to WWU
Might have some useful scripts when doing analyses.

./build_refpkg
This dir contains the scripts Ryan use to build the 2014 refpkgs.
These are not updated to run on HTCondor, but will work on SGE

./htc_config
This dir currently only contains the machines file use when using the make_nest script in analyze_meta.

./prep_seq
This dir contains any sequence prep scripts for preparing your metagenome for an analysis.


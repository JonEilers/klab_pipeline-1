# klab_pipeline
Combination of the good parts of DAP and package_compare.

## bin
Shell scripts which are convenience wrappers around python scripts for common tasks.

## python packages
 * **klab.process**
    - jplace files -> pandas data frames
    - taxonomical lineage
    - derived information (counts, confidence type)
 * **klab.analysis** - the good stuff, what happens after processing
    - diversity
    - edpl 
 * **lib**
    - third party code    
 * **cookbook** - one-off code that was useful for something and might be again
    - **junk_drawer** - Ryan's quick dump of DAP code, to be organized later
 * **data** (okay, not a package but used by them)
    - NCBI data and code to fetch it
 

## Other packages (probably)
 * **klab.translation**
    - importers and exporters to communicate with third party software
 * **klab.plot** (graph?)
    - graphing routines to have some standards
    - bar
    - scatter
    - heatmap

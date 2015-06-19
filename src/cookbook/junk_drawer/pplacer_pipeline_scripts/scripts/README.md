# Creating Reference Packages

## Recruiting sequences

The script `kaboodle-search-recruit` recruits sequences to a set of HMMs using
a single run of `hmmsearch`.  It should be run as an MPI job on the cluster through a shell
script.  An example shell script is at `scripts/making/make_nest.sh`.  In
experimentation, 48 cores seem to be saturated (100% CPU usage on all nodes),
 but 128 are not.

The tree building program is specified at recruit time using a flag to
kaboodle-search-recruit. See `kaboodle-search-recruit -h` for details.

`kaboodle-search-recruit` assigns each sequence that matches 1+ HMM to the HMM
with highest domain bit score.  

A nested directory structure is created with any HMMs with 1+ sequence hits from the database.

## Building reference packages for recruited sequences

Once sequences are recruited, run `scripts/making/do_nestrun.sh` to
perform the reference package building (tree inference, masking, etc).
Some parameters may need to be changed on a per-run basis.

# Analyzing Sequences

The script `kaboodle-search-analysis` recruits sequences to a set of reference package HMMs using
a single run of `hmmsearch`.  It should be run as an MPI job on the cluster through a shell
script. Almost all behavior is identical to `kaboodle-search-recruit`, except:

* The arguments are directories of reference packages, rather than HMMs
* The nest built of the results contains different keys (refpkg, etc)

A nested directory structure is created for any reference packages with
1+ sequence hits, containing a nestly control file and the hit(s).

An example script to make a nested directory structure for analysis is
in `scripts/analysis/make_nest.sh`.

Once sequences are recruited to reference packages, run
`scripts/analysis/do_nestrun.sh` to submit the pplacer jobs to the
cluster.

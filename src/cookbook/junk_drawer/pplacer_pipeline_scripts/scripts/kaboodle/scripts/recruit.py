"""
Run an hmmsearch against a set of HMMs, build infrastructure for
reference package building
"""

import argparse
import json
import logging
import os
import os.path
import shutil
import sys

from kaboodle import hmmer
from kaboodle.hmmer import hmm_name
from kaboodle.scripts import floatish, extant_file, joiner, stripext

def combine_hmms(hmm_paths, output_fp):
    """
    Combine the hmms in hmm_paths, write to output_fp.

    Returns a dictionary mapping HMM name -> hmm_path
    """
    d = {}
    for hmm in hmm_paths:
        with open(hmm) as hmm_fp:
            try:
                name = hmm_name(hmm_fp)
            except IOError:
                continue
            # Rewind, copy all contents
            hmm_fp.seek(0)
            shutil.copyfileobj(hmm_fp, output_fp)

            if name in d:
                raise ValueError("Two HMMs are named {0} ({1} {2})".format(
                                    name, hmm, d[name]))
            d[name] = hmm

    return d


def main(args=sys.argv[1:]):
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--force', help="""Overwrite files""",
            action='store_true')
    parser.add_argument('-E', '--max-e-value', default='1e-5',
            help="""Maximum e-value to recruit a sequence [default:
            %(default)s]. Applied *per domain*.""", type=floatish)
    parser.add_argument('--tree-method', choices=('fasttree', 'raxml'),
        default='fasttree', help="""Method to save in control file for building
        trees [Default: %(default)s]""")
    parser.add_argument('--mpi-exec', default='mpirun',
            help="""Name of executable to run MPI [default: %(default)s]""")

    parser.add_argument('sequence_file', help="""Sequence file""",
            type=extant_file)
    parser.add_argument('--run-dir', help="""Prefix for output reference
            packges [default: %(default)s]""", default='runs')

    parser.add_argument('hmms', metavar='hmm_file',
            help="""HMM files to include in search.""", nargs='+')

    arguments = parser.parse_args(args)

    p = joiner('recruit')

    hmm_name = 'combined.hmm'
    hmm_path = p(hmm_name)

    if not os.path.isdir(p()):
        os.makedirs(p())

    assert arguments.force or not os.path.exists(hmm_path), \
            'Combined HMM exists! ' + hmm_path
    with open(hmm_path, 'w') as fp:
        logging.info('Combining HMMs to %s', hmm_path)
        # Merge all HMMs. Map allows use of the reference package later
        hmm_map = combine_hmms(arguments.hmms, fp)

    with open(p('hmm_map.json'), 'w') as fp:
        json.dump(hmm_map, fp, indent=2)

    domtblout = p(stripext(arguments.sequence_file) + '.domtblout')

    hmmer.hmmsearch(hmm_path, arguments.sequence_file, domtblout=domtblout,
                    max_e_value=arguments.max_e_value,
                    mpi_command=arguments.mpi_exec)
    logging.info('done')

if __name__ == '__main__':
    main()


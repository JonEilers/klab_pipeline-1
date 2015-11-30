#!/usr/bin/env python
"""
Run an hmmsearch against a set of reference packages, build infrastructure for
pplacer analysis
"""

import argparse
import json
import logging
import os
import os.path
import shutil
import sys

from Bio import SeqIO

from taxtastic.refpkg import Refpkg
from kaboodle.hmmer import hmm_name, recruit_sequences, IndexedSequenceFetcher
from kaboodle.scripts import floatish, extant_file, joiner, stripext


def search_for_refpkgs(d):
    """
    Search for reference packages under directory d
    Returns generator of paths
    """
    if not os.path.isdir(d):
        raise ValueError("Path {0} does not exist. Cannot search for refpkgs".format(d))
    return (os.path.abspath(p) for p, _, fs in os.walk(d)
            if 'CONTENTS.json' in fs)


def combine_refpkg_hmms(refpkg_paths, output_fp):
    """
    Combine the reference packages in refpkg_paths, write to output_fp.

    Returns a dictionary mapping HMM name -> refpkg_path
    """
    d = {}
    for refpkg_path in refpkg_paths:
        r = Refpkg(refpkg_path)
        hmm = r.file_abspath('profile')
        with open(hmm) as hmm_fp:
            name = hmm_name(hmm_fp)
            # Rewind, copy all contents
            hmm_fp.seek(0)
            shutil.copyfileobj(hmm_fp, output_fp)

            if name in d:
                raise ValueError("Two reference package HMMs are "
                                 "named {0} ({1} {2})".format(
                    name, refpkg_path, d[name]))
            d[name] = refpkg_path

    return d


def build_nest(recruited_refpkgs, sequence_database_path, run_dir='analysis',
               base_dict=None, file_name='recruit.fasta'):
    def refpkg_label(s):
        s = os.path.basename(s)
        if s.endswith('.refpkg'):
            s = s[:len(s) - len('.refpkg')]
        return s

    # Build the nest
    logging.info('Building nest under %s', run_dir)
    fetcher = IndexedSequenceFetcher(sequence_database_path)
    for refpkg, sequence_ids in recruited_refpkgs:
        sequence_ids = list(sequence_ids)
        control = (base_dict or {}).copy()
        control['refpkg'] = refpkg
        control['title'] = refpkg_label(refpkg)

        control['n_sequences'] = len(sequence_ids)
        control['seq_file'] = file_name

        d = os.path.join(run_dir, control['title'])
        if not os.path.isdir(d):
            os.makedirs(d)
        p = joiner(d)

        # Generate control file
        with open(p('control.json'), 'w') as fp:
            json.dump(control, fp, indent=2)
            fp.write('\n')

        # Write sequences
        sequences = fetcher.extract_best_hits(sequence_ids)
        count = SeqIO.write(sequences, p(file_name), 'fasta')
        assert count > 0, 'No sequences written to {0}'.format(p(file_name))


def main(args=sys.argv[1:]):
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('-f', '--force', help="""Overwrite files""",
                        action='store_true')
    parser.add_argument('-E', '--max-e-value', default='1e-5',
                        help="""Maximum e-value to recruit a sequence [default:
            %(default)s]""", type=floatish)
    parser.add_argument('--mpi-exec', default='mpirun',
                        help="""Name of executable to run MPI [default: %(default)s]""")

    parser.add_argument('sequence_file', help="""Sequence file""",
                        type=extant_file)
    parser.add_argument('--run-dir', help="""Prefix for output reference
            packges [default: %(default)s]""", default='analysis')
    parser.add_argument('--recruit-dir', help="""Directory for HMM / recruiting
            sequences""", default='recruit')

    parser.add_argument('refpkg_dirs', metavar='refpkg_dir', help="""Directory
        containing reference packages. Directory will be searched for reference
        packages. Any reference package found will be included. Multiple
        directories may be specified.""", nargs='+')

    arguments = parser.parse_args(args)

    p = joiner(arguments.recruit_dir)

    hmm_name = '_'.join(os.path.basename(d) for d in
                        arguments.refpkg_dirs)[:50] + '.hmm'
    hmm_path = p(hmm_name)
    reference_packages = (r for d in arguments.refpkg_dirs
                          for r in search_for_refpkgs(d))

    if not os.path.isdir(p()):
        os.makedirs(p())

    assert arguments.force or not os.path.exists(hmm_path), \
        'Combined HMM exists! ' + hmm_path
    with open(hmm_path, 'w') as fp:
        logging.info('Combining HMMs to %s', hmm_path)
        # Merge all HMMs. Map allows use of the reference package later
        hmm_map = combine_refpkg_hmms(reference_packages, fp)

    if not hmm_map:
        raise ValueError("No reference packages found under {0}".format(arguments.refpkg_dirs))

    domtblout = p(stripext(arguments.sequence_file) + '.domtblout')

    recruited = recruit_sequences(hmm_path, arguments.sequence_file, domtblout,
                                  arguments.max_e_value, arguments.mpi_exec)
    recruited_refpkgs = ((hmm_map[hmm], sequences) for hmm, sequences in recruited)

    build_nest(recruited_refpkgs, arguments.sequence_file, run_dir=arguments.run_dir,
               base_dict={'sequence_file_analyzed': arguments.sequence_file})


if __name__ == '__main__':
    main()

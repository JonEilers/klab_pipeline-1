"""
Build a nested directory structure using the results of an HMMSEARCH
"""

import argparse
import json
import logging
import os
import os.path
import sys

from Bio import SeqIO

from kaboodle import hmmer
from kaboodle.scripts import extant_file, joiner, stripext

def build_nest(recruited_hmms, sequence_database_file,
        run_dir='runs', base_dict=None,
        file_name='recruit.fasta'):
    # Build the nest, by hand
    logging.info('Building nest under %s', run_dir)
    fetcher = hmmer.IndexedSequenceFetcher(sequence_database_file)
    for hmm, sequence_ids in recruited_hmms:
        sequence_ids = list(sequence_ids)
        control = (base_dict or {}).copy()
        control['seed_hmm'] = hmm
        control['title'] = stripext(hmm)
        control['seq_file'] = file_name

        d = os.path.join(run_dir, control['title'])
        if not os.path.isdir(d):
            os.makedirs(d)
        p = joiner(d)
        with open(p('control.json'), 'w') as fp:
            json.dump(control, fp, indent=2)
            fp.write('\n')

        sequences = fetcher.extract_best_hits(sequence_ids)
        count = SeqIO.write(sequences, p(file_name), 'fasta')
        assert count > 0, 'No sequences written to {0}'.format(count)

def main(args=sys.argv[1:]):
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--tree-method', choices=('fasttree', 'raxml'),
        default='fasttree', help="""Method to save in control file for building
        trees [Default: %(default)s]""")

    parser.add_argument('sequence_file', help="""Sequence file""",
            type=extant_file)
    parser.add_argument('--run-dir', help="""Prefix for output reference
            packges [default: %(default)s]""", default='runs')

    parser.add_argument('dom_tbl', help='HMMSEARCH domtblout')
    parser.add_argument('hmm_map', help='JSON mapping from HMM name to path')

    arguments = parser.parse_args(args)

    with open(arguments.hmm_map) as fp:
        hmm_map = json.load(fp)

    with open(arguments.dom_tbl, 'r', buffering=8<<20) as fp:
        results = hmmer.domtbl_parse(fp)
        best_hits = hmmer.choose_best_hit(results)[0]
    logging.info('%d best_hits', len(best_hits))

    grouped = hmmer.sequences_by_hmm(best_hits)
    grouped = ((hmm_map[k], v) for k, v in grouped)

    build_nest(grouped, arguments.sequence_file, run_dir=arguments.run_dir,
               base_dict={'sequence_file_analyzed': arguments.sequence_file,
                          'tree_method': arguments.tree_method})

if __name__ == '__main__':
    main()


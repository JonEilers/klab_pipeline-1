#!/home/mclaugr4/software/bin/python

import argparse
import collections
import csv
import itertools
import os.path
import re
import sys

from Bio import SeqIO
#import networkx
from taxtastic import refpkg

RANGE_RE = re.compile(r'/\d+-\d+$')

def strip_range(sequence_id):
    """
    >>> strip_range('1234|gi|44562/45-60')
    '1234|gi|44562'
    """
    return RANGE_RE.sub('', sequence_id)

def find_repeated_sequences(reference_packages):
    seen_sequences = collections.defaultdict(list)
    for r in reference_packages:
        with r.resource('aln_fasta') as fp:
            for i in (strip_range(s.id) for s in SeqIO.parse(fp, 'fasta')):
                seen_sequences[i].append(r.path)
    return {k:v for k, v in seen_sequences.items() if len(v) > 1}

#def generate_graph(multi_seq):
    #g = networkx.MultiGraph()
    #edges = collections.defaultdict(list)
    #for sequence, refpkgs in multi_seq:
        #comb = itertools.combinations(refpkgs, 2)
        #for s in comb:
            #s = frozenset(s)
            #edges[s].append(sequence)

    #for (a, b), sequences in edges.items():
        #g.add_edge(a, b, label=len(sequences))

    #return g

def write_results(multi_seq, output):
    rows = ((k, ','.join(os.path.basename(i) for i in v))
            for k, v in multi_seq.items())
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(('sequence', 'refpkgs'))
    writer.writerows(rows)

def main():
    parser = argparse.ArgumentParser(description="""Find sequences in multiple
    reference packages""")
    parser.add_argument('reference_packages', metavar='refpkg', nargs='+',
            type=refpkg.Refpkg)
    parser.add_argument('-o', '--output', default=sys.stdout,
            help='Destination',
            type=argparse.FileType('w'))

    arguments = parser.parse_args()

    # Filter those seen multiple times
    seen_sequences = find_repeated_sequences(arguments.reference_packages)
    with arguments.output:
        write_results(seen_sequences, arguments.output)

if __name__ == '__main__':
    main()

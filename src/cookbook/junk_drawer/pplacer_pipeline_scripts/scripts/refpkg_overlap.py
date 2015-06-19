#!/home/mclaugr4/software/bin/python
"""
Find overlaps between reference packages
"""

import argparse
import csv
import itertools
import os.path
import re
import sys

from Bio import SeqIO
from taxtastic import refpkg

RANGE_RE = re.compile(r'/\d+-\d+$')

def strip_range(sequence_id):
    """
    >>> strip_range('1234|gi|44562/45-60')
    '1234|gi|44562'
    """
    return RANGE_RE.sub('', sequence_id)

def stripext(f):
    return os.path.splitext(os.path.basename(f))[0]

def sequence_contents(reference_packages):
    def inner(refpkg):
        with open(refpkg.file_abspath('aln_fasta')) as fp:
            return frozenset(strip_range(s.id) for s in SeqIO.parse(fp, 'fasta'))

    return {stripext(r.path): inner(r) for r in reference_packages}

def find_overlap(contents):
    result = {}
    for (i_name, i_seqs), (j_name, j_seqs) in itertools.combinations(contents.items(), 2):
        overlap = len(i_seqs & j_seqs)
        if overlap:
            key = tuple(sorted((i_name, j_name)))
            result[key] = (overlap, len(i_seqs), len(j_seqs))

    return result

def write_results(multi_seq, output):
    rows = (list(k) + list(v)
            for k, v in multi_seq.items())
    writer = csv.writer(output, delimiter='\t')
    writer.writerow(('refpkg1', 'refpkg2', 'overlap_size', 's1', 's2'))
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
    contents = sequence_contents(arguments.reference_packages)
    overlap = find_overlap(contents)
    with arguments.output:
        write_results(overlap, arguments.output)

if __name__ == '__main__':
    main()

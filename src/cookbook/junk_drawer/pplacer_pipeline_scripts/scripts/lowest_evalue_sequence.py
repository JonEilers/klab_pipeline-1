#!/home/mclaugr4/software/bin/python
"""
Returns the lowest scoring sequence per domain
"""

import argparse
import itertools
import operator

from Bio import SeqIO


class IterCounter(object):
    def __init__(self, iterable):
        self.iterable = iterable
        self.count = 0

    def __iter__(self):
        return self

    def next(self):
        self.count += 1
        return next(self.iterable)


def highest_scoring(domain_table):
    """
    Gets a set of the lowest e-values by domain
    """

    def key(line):
        """Sort by independent E-value"""
        return float(line[12])

    def new_id(line):
        """
        Mirrors the ID in a .sto file from a row in a domain table:

            ID/start-end
        """
        return "{0}/{1}-{2}".format(line[0], line[17], line[18])

    lines = iter(domain_table)
    lines = (i.rstrip('\n') for i in lines if not i.startswith('#'))
    split_lines = (i.split() for i in lines)
    grouped = itertools.groupby(split_lines, operator.itemgetter(0))

    result = set(new_id(sorted(list(l), key=key)[0]) for g, l in grouped)
    return result


def filter_seqs(sequences, keep_ids):
    """
    Keep sequences specified in keep_ids, discarding the rest
    """
    for sequence in sequences:
        if sequence.id in keep_ids:
            yield sequence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('stockholm_file', type=argparse.FileType('r'))
    parser.add_argument('domain_table', type=argparse.FileType('r'),
                        help='Output of hmmsearch --domtblout')

    parser.add_argument('output_file', type=argparse.FileType('w'))
    arguments = parser.parse_args()

    with arguments.domain_table as domain_table:
        keep_sequence_ids = highest_scoring(domain_table)

    with arguments.stockholm_file as infile:
        seq_counter = IterCounter(SeqIO.parse(infile, 'stockholm'))
        sequences = iter(seq_counter)
        sequences = filter_seqs(sequences, keep_sequence_ids)
        with arguments.output_file as outfile:
            count = SeqIO.write(sequences, outfile, 'stockholm')

    print 'Kept {0}/{1} sequences'.format(count, seq_counter.count)


if __name__ == '__main__':
    main()

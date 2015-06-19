#!/home/mclaugr4/software/bin/python
"""
Little script to verify that taxids can be parsed from a sequence file.

"""
import argparse
import collections
import sqlite3
import sys

from Bio import SeqIO

def load_taxids(taxonomy_db_path):
    command = "SELECT tax_id FROM nodes;"
    connection = sqlite3.connect(taxonomy_db_path)
    try:
        cursor = connection.cursor()
        cursor.execute(command)
        return set(int(i[0]) for i in cursor)
    finally:
        connection.close()


def check_taxids(taxids, sequences):
    ids = (sequence.id for sequence in sequences)
    counter = collections.Counter({'UNKNOWN':0, 'INVALID':0, 'OK':0})
    ok = 0
    invalid = 0
    unknown = 0
    for i in ids:
        try:
            taxid = int(i.split('|')[0])
            c = 'OK' if taxid in taxids else 'UNKNOWN'
        except ValueError:
            taxid = i
            c = 'INVALID'

        if c != 'OK':
            print '\t'.join(map(str, (c + ' taxid', taxid, i)))
        counter[c] += 1

    return counter


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input-format', default='fasta',
        help="""Input sequence format (default: %(default)s)""")
    parser.add_argument('taxonomy_db', help='sqlite taxonomy db')
    parser.add_argument('sequence_file', type=argparse.FileType('r'))

    arguments = parser.parse_args(argv)

    taxids = load_taxids(arguments.taxonomy_db)

    with arguments.sequence_file:
        sequences = SeqIO.parse(arguments.sequence_file, arguments.input_format)
        counts = check_taxids(taxids, sequences)

    for i, j in counts.items():
        print >> sys.stderr, 'Total {0}: {1}'.format(i, j)

    sys.exit(sum(counts.values()) == counts['OK'])


if __name__ == '__main__':
    main()


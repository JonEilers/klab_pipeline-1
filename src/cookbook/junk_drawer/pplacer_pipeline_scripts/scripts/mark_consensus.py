#!/home/mclaugr4/software/bin/python
"""
Make a sto file with a GC RF line which indicates that it's either in the mask or the column is a consensus column
"""
import argparse
import itertools
import os
import re

from Bio import AlignIO, Seq, SeqIO


def compress_sequences(sequences, mask):
    for sequence in sequences:
        s = sequence[:]
        s.seq = Seq.Seq(''.join(itertools.compress(str(s.seq), mask)))
        yield s


def get_nongap_frac(align, gap='-'):
    """
    Gets the fraction of sequences by column in an alignment
    which are not gap characters
    """
    length = align.get_alignment_length()
    nseqs = len(align)
    columns = [align[:, i] for i in xrange(length)]
    nongap = [sum(b not in gap for b in col) for col in columns]
    return [float(x) / nseqs for x in nongap]


def int_list_of_file(handle):
    """
    Get a comma-delimited integer list from a file, ignoring newlines and
    whitespace
    """
    # Regex to remove whitespace from mask file.
    whitespace = re.compile(r'\s|\n', re.MULTILINE)
    mask_text = handle.read()
    mask_text = re.sub(whitespace, '', mask_text)

    # Cast mask positions to integers
    return map(int, mask_text.split(','))


def trans_bool(b):
    """
    Turn a boolean into a consensus annotation

    True  -> x
    False -> .
    """
    return 'x' if b else '.'


def rf_of_bool_list(bl):
    return "".join(map(trans_bool, bl))


def write_gc_rf_sto(out_name, align, is_consensus):
    with open(out_name, "w") as handle:
        handle.write("# STOCKHOLM 1.0\n\n")
        for record in align:
            handle.write(record.id + "  " + re.sub("\?", "~", str(record.seq)) + "\n")
        handle.write("#=GC RF  " + rf_of_bool_list(is_consensus) + "\n")
        handle.write("//\n")


def update_mask_positions(updated_consensus, mask_positions):
    """
    Update mask positions to be relative to updated_consensus
    """
    c = itertools.count().next
    # Create a list with mask indexes
    v = [c() if i else None for i in updated_consensus]
    result = [v[i] for i in mask_positions]
    assert all(i is not None for i in result)
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--consensus-threshold', type=float, default=0.5,
                        help='''Minimum proportion of non-gap bases to consider a consensus
            column (default: %(default)s''')
    parser.add_argument('fasta_name', help='fasta_file', type=argparse.FileType('r'))
    parser.add_argument('mask_file', help='Mask file', type=argparse.FileType('r'))
    parser.add_argument('--stockholm-out')
    parser.add_argument('--masked-out')
    parser.add_argument('output_mask', help='New mask file', type=argparse.FileType('w'))

    arguments = parser.parse_args()
    with arguments.fasta_name:
        align = AlignIO.read(arguments.fasta_name, 'fasta')

    # Make a list of consensus columns
    is_consensus = [x > arguments.consensus_threshold
                    for x in get_nongap_frac(align)]

    # Add positions in mask_file
    with arguments.mask_file:
        in_mask_positions = int_list_of_file(arguments.mask_file)
    # trim trailing 0's, sometimes added by trimal
    in_mask_positions = [p for i, p in enumerate(in_mask_positions) if i == 0 or p > 0]

    # Mark positions from in_mask_positions to consensus positions
    for in_mask_pos in in_mask_positions:
        is_consensus[in_mask_pos] = True

    # Make a new mask, indexed by consensus position
    new_in_mask = update_mask_positions(is_consensus, in_mask_positions)

    with arguments.output_mask as fp:
        print >> fp, ','.join(str(i) for i in new_in_mask)

    if arguments.stockholm_out:
        stockholm_out = arguments.stockholm_out
    else:
        stockholm_out = os.path.splitext(arguments.fasta_name.name)[0] + '.sto'

    write_gc_rf_sto(stockholm_out, align, is_consensus)

    if arguments.masked_out:
        m = [i in in_mask_positions for i in xrange(len(align[0]))]
        SeqIO.write(compress_sequences(align, m), arguments.masked_out, 'fasta')


if __name__ == '__main__':
    main()

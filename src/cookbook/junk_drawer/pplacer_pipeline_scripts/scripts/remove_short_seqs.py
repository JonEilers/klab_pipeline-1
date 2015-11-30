#!/home/mclaugr4/software/bin/python
"""Clean up an alignment fasta file.

Inspired by Chris' version, but rewritten from scratch.

Input:
Fasta file must have taxonomic IDs as the first column
in sequence ID lines.
e.g. 435258 is a taxonomic ID in the following line
435258|gi|146090538|ref|XP_001470604.1|Leishmania_infantum

Output:
STDOUT, cleaned aligned multiple fasta.

Features:
- Remove exact duplicate alignment sequences (keep first seen only).
- Remove short alignments based on a minimum fraction of non-gap characters.
- Remove duplicate taxonomic entries (keep first seen only).
- Remove illegal characters from IDs.
- Replace ? gap character with -.
- Replace ~ gap characeter with - (created by BioEdit).

"""
import os
import sys

from Bio import SeqIO, AlignIO

min_nongap = 0.2
nastychars = """[]();,:'"+"""
seq_to_remove = """.?~-*"""


def taxid_of_record(record):
    return (int(record.id.split("|")[0]))


def remove_short_seqs(seed_len, records):
    """
    SeqRecord iterator to remove short sequences. Note that gap is - here.
    """
    for record in records:
        if (float(len(str(record.seq).translate(None, '-'))) / seed_len) < min_nongap:
            print "Ignoring too short seq %s" % record.id
            continue
        yield record


def sto_len(fname):
    with open(fname, 'r') as ch:
        return AlignIO.read(ch, "stockholm").get_alignment_length()


seed_sto = sys.argv[1]
assert (".sto" == os.path.splitext(seed_sto)[1]);
seed_len = sto_len(seed_sto)

for fname in sys.argv[2:]:
    base, ext = os.path.splitext(fname)
    assert ext == ".fasta" or ext == ".afa"
    records = remove_short_seqs(seed_len, SeqIO.parse(fname, "fasta"))
    count = SeqIO.write(records, base + ".tidy.fasta", "fasta")

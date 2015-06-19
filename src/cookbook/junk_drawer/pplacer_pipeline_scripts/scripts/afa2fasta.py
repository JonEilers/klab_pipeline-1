#!/home/mclaugr4/software/bin/python
"""
Convert the HMMER afa files to fasta, i.e. make gaps -, and take only the first part of the name without whitespace.
"""
import sys, os, string
from Bio import SeqIO, AlignIO
from Bio.Seq import Seq, SeqRecord

seqtrans = string.maketrans(".", "-")

def convert(records):
    """
    SeqRecord iterator to make all gaps -'s and take only the first
    nonwhitespace name.
    """
    for record in records:
        yield SeqRecord(Seq(str(record.seq).translate(seqtrans)),
                id=record.id.split(" ")[0],
                description="")

for fname in sys.argv[1:]:
    (base, ext) = os.path.splitext(fname)
    assert(ext == ".afa")
    count = SeqIO.write(convert(SeqIO.parse(fname, "fasta")), base+".fasta",
            "fasta")

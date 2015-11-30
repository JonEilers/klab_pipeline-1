#!/share/apps/python2.5/bin/python

import sys
import os

from Bio import SeqIO
from Bio import Translate
from Bio.Seq import Seq
from Bio.Alphabet import IUPAC

args = sys.argv
del args[0]  # get rid of name of script

std_trans = Translate.unambiguous_dna_by_id[1]

for fname in args:

    base = os.path.splitext(fname)[0]
    inFile = open(fname, 'r')
    outFile = open(base + ".6tr.fasta", 'w')
    for cur_record in SeqIO.parse(inFile, "fasta"):
        for frame in [0, 1, 2]:
            outFile.write(">%s_frame%d\n" % (cur_record.name, frame))
            unambSeq = Seq(str(cur_record.seq)[frame:], IUPAC.unambiguous_dna)
            outFile.write(str(std_trans.translate(unambSeq)) + "\n")

        for frame in [0, 1, 2]:
            outFile.write(">%s_rvcmp%d\n" % (cur_record.name, frame))
            revCompSeq = Seq(str(cur_record.seq.reverse_complement())[frame:], IUPAC.unambiguous_dna)
            outFile.write(str(std_trans.translate(revCompSeq)) + "\n")
    inFile.close()

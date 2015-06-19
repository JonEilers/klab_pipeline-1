#!/home/mclaugr4/software/bin/python
"""
Make CSV file mapping sequence names to tax ids

e.g. 435258 is a taxonomic ID in the following line
435258|gi|146090538|ref|XP_001470604.1|Leishmania_infantum
"""
import sys, os, string
from Bio import SeqIO, AlignIO

for fname in sys.argv[1:]:
    (base, _) = os.path.splitext(fname)
    csv_file = open(base+".tax_map.csv",'w')
    csv_file.write("tax_id,seqname\n")

    taxids = set()

    for record in SeqIO.parse(fname, "fasta"):
        taxid = record.id.split("|")[0]
        try:
            taxid = int(taxid)
            taxids.add(taxid)
        except ValueError:
            print >> sys.stderr, "Couldn't parse taxid:", taxid
        csv_file.write(record.id.split("|")[0] + "," + record.id + "\n")

    csv_file.close()

    ids_file = open(base+".ids_only",'w')

    for id in taxids:
        ids_file.write(str(id) + "\n")

    ids_file.close()

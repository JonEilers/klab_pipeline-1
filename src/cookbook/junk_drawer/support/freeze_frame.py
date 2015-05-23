from Bio import SeqIO
from Bio.Seq import reverse_complement, translate, Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC
import sys

def sub_lst(lst,len_lst,a):
    get_ind = [i for i, x in enumerate(len_lst) if x == a]
    return [lst[i] for i in get_ind]

def sf(seq,genetic_code=1):
	anti = reverse_complement(seq) 
	comp = anti[::-1] 
	length = len(seq) 
	frames = []
	min_len = 30
	for i in range(0, 3): 
		fragment_length = 3 * ((length-i) // 3)
		trans1 = translate(seq[i:i+fragment_length],genetic_code)
		for seg in trans1.split('*'):
			if len(seg)*3 >= min_len:
				frames.append(seg)
		trans2 = translate(anti[i:i+fragment_length],genetic_code)[::-1]
		for seg in trans2.split('*'):
			if len(seg)*3 >= min_len:
				frames.append(seg)
	return frames

nuc_fasta = sys.argv[1]
outfile = sys.argv[2]
with open(outfile,'w') as o:
	for record in SeqIO.parse(open(nuc_fasta), 'fasta'):
		id,sequence = record.id, record.seq.tostring()
		new_sequence = sf(sequence)
		counter = 1
		for ns in new_sequence:
			name = record.name
			description = record.description
			record = SeqRecord(Seq(ns, IUPAC.protein),
			id=id + '_' + str(counter), name=name, description=description)
			SeqIO.write(record, o, 'fasta')
			counter += 1
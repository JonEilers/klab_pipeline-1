from os import path, listdir
import subprocess
import re
from Bio import SeqIO
from Bio.Seq import Seq
from Bio.SeqRecord import SeqRecord
from Bio.Alphabet import IUPAC

def div_fast(seqs, n):
	avg = len(seqs) / float(n)
	out = []
	last = 0.0
	while last < len(seqs):
		out.append(seqs[int(last):int(last + avg)])
		last += avg
	# deal with remainders
	if len(out) > n:
		end = out[-1]
		del out[-1]
		print end
		out[-1].extend(end)
	return out


def clean_str(string):
	rx = '[' + re.escape(''.join([':',';','.',',','-',' '])) + ']'
	trim_string = re.sub(rx, '_', string)
	return trim_string


# paths
fastq_path = '/share/research-groups/kodner/data_files/BB_OMZ/fastq'
fasta_path = '/share/research-groups/kodner/data_files/BB_OMZ/fasta'

# convert fastq to fasta

file_list = listdir(fastq_path)
for fastq in file_list:
	if fastq.find('.fastq') != -1:
		full_fastq = path.join(fastq_path, fastq)
		fasta = '.'.join([fastq.split('.')[0], 'fasta'])
		full_fasta = path.join(fasta_path, fasta)
		subprocess.call(['seqmagick', 'convert', full_fastq, full_fasta])
		print fastq, 'converted...'

# modify fasta seq names
file_list = listdir(fasta_path)
new_list = []
for file in file_list:
	if file.find('.fasta') != -1 and file.find('.proc') == -1 and file.find('R2') == -1:
		print file
		for record in SeqIO.parse(path.join(fasta_path, file), 'fasta'):
			ID, description, sequence = record.id, record.description, str(record.seq)
			new_ID = '|'.join([file.rsplit('.',1)[0], ID])
			new_list.append((clean_str(new_ID), clean_str(description.rsplit(' ', 1)[1]), sequence))

# split fasta seqs into n equal[ish] files
div_fastas = div_fast(new_list, 1) ## TODO: finsih this dividing section

x = 0
for seq_list in div_fastas:
	print x, len(seq_list)
	output_handle =  open(''.join(['meta_', str(x), '.fasta']), 'w')
	for seq in seq_list:
		entry = SeqRecord(Seq(seq[2], IUPAC.unambiguous_dna), id=seq[0], description=seq[1])
		SeqIO.write(entry, output_handle, 'fasta')
	output_handle.close()
	x += 1

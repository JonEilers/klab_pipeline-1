import os
import sys
from qsub import Qsub

write_dir = sys.argv[1]
# /share/research-groups/kodner/TARA/
script_path = sys.argv[2]
# /share/research-groups/kodner/klab_pipeline/src/cookbook/fasta_filtering.py
ncbi_dir = sys.argv[3]
# /share/research-groups/kodner/klab_pipeline/src/data/
alignment_dir = sys.argv[4]
# share/research-groups/kodner/TARA/COG_alignments/

def slice_it(script_cmd_list,file_number):
	sub_lists = []
	start = 0
	for i in xrange(file_number):
		stop = start + len(script_cmd_list[i::file_number])
		sub_lists.append(script_cmd_list[start:stop])
		start = stop
	return(sub_lists)

qsub_dir = write_dir + '/qsub_scripts/'
if not os.path.exists(qsub_dir):
	os.makedirs(qsub_dir)

fasta_file_list = [root + '/' + fasta for root, dirs, fastas in os.walk(alignment_dir) for fasta in fastas if fasta.split('.')[-1].find('fasta') != -1]
script_cmd_list = []
file_number = 7
for fasta in fasta_file_list:
	script_cmd = ' '.join(['python', script_path, ncbi_dir,fasta,alignment_dir])
	script_cmd_list.append(script_cmd)
# break the script commands into [file_number] of qsub scripts
sub_lists = slice_it(script_cmd_list,file_number)
for script_cmd_list in sub_lists:
	file_name = 'qsub_filter' + str(sub_lists.index(script_cmd_list))
	qsub_file = Qsub(qsub_dir, script_cmd_list, file_name)
	print qsub_file.Batch_builder()

qsub_file_list = os.listdir(qsub_dir)
for qsub_file in qsub_file_list:
	if qsub_file.find('.sh') != -1:
		os.system('qsub ' + qsub_dir + qsub_file)
		print qsub_file, 'has been sent to the cluster...'

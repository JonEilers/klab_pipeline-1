import os
from qsub import Qsub


def slice_it(script_cmd_list,file_number):
	sub_lists = []
	start = 0
	for i in xrange(file_number):
		stop = start + len(script_cmd_list[i::file_number])
		sub_lists.append(script_cmd_list[start:stop])
		start = stop
	return(sub_lists)

path = '/home/mclaugr4/bio/refpkg_project_071414/makerefs/'
qsub_file_path = path + 'qsubs/'
dir = path + 'runs/'
'''
dir_list = os.walk(dir)
for root,dirs,files in dir_list:
	for file in files:
		if file.find('.fasta'):
			file = root + '/' + file
			os.system('qsub /home/mclaugr4/software/bin/python ' + 
						path + 'find_bad_taxit.py ' + file)
'''
#Create SBE QSUB BATCH scripts from the fasta file list
fasta_file_list = [root + '/' + fasta for root, dirs, fastas in os.walk(dir) for fasta in fastas if fasta.split('.')[-1].find('fasta') != -1]
script_cmd_list = []
file_number = 192
for fasta in fasta_file_list:
	script_cmd = ' '.join(['/home/mclaugr4/software/bin/python',
						path + 'find_bad_taxit.py',fasta
							])
	script_cmd_list.append(script_cmd)
# break the script commands into [file_number] of qsub scripts
sub_lists = slice_it(script_cmd_list,file_number)
for script_cmd_list in sub_lists:
	file_name = 'qsub_' + str(sub_lists.index(script_cmd_list))
	qsub_file = Qsub(qsub_file_path, script_cmd_list, file_name)
	print qsub_file.Batch_builder()

qsub_file_list = os.listdir(qsub_file_path)
for qsub_file in qsub_file_list:
	if qsub_file.find('.sh') != -1:
		os.system('qsub ' + qsub_file_path + qsub_file)
		print qsub_file, 'has been sent to the cluster...'

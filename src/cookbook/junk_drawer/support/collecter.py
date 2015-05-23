import os, sys

path = '/home/mclaugr4/bio/DAP/test_data/prePAF/'
translation_path = path + 'translated_data/'

trans_list = os.listdir(translation_path)

output = open(path + 'Supragenome.fasta', 'w')
out_dictionary = {}
repeat_list = []
for file in trans_list:
	if file.find('.unq.') != -1:
		input = open(translation_path + file, 'r')
		for line in input:
			output.write(line)
		input.close()
		print file, 'has been added to the Supragenome file...'
output.close()
print repeat_list

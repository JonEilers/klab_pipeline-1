import os,sys

homepath = os.path.dirname(os.path.realpath(__file__))
jplace_path = homepath + '/COG_jplace/'
jplace_split_out_path = homepath + '/jplace_split/'

input = ['B6', 'B7', 'B8', 'B11', 'B12', 'B13']

jplace_file_list = os.listdir(jplace_path)
#jplace_split_list = os.listdir(jplace_split_out_path)

for jplace_file in jplace_file_list:
	for index in range(0, len(input)):
		keep_value = input[index]
		guppy_cmd = '/home/mclaugr4/software/bin/guppy filter -Ir ' + keep_value
		for index_2 in range(0, len(input)):
			if index != index_2:
				remove_value = input[index_2]
				guppy_cmd = guppy_cmd + ' -Er ' + remove_value
		#jplace_split_list = os.listdir(jplace_split_out_path)
		#if jplace_split_list.count(keep_value) == 0:
		#	os.system('mkdir ' + jplace_split_out_path + keep_value)
		guppy_cmd = str(guppy_cmd + ' ' + jplace_path + jplace_file + ' -o ' + 
			jplace_split_out_path + 
			jplace_file.split('/')[-1].split('.')[0] + '.' + keep_value + '.jplace'
			)
		print guppy_cmd
		os.system(guppy_cmd)



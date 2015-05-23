import os,sys

homepath = os.path.dirname(os.path.realpath(__file__))
working_dir = homepath + '/data/ETSP_SSU/'
jplace_path = '/home2/mclaugr4/Thesis_ETSP/SSU_jplace_03-18-2015/'
jplace_split_out_path = working_dir + 'jplace_split/'

input = ['SRR064444','SRR064445','SRR064446','SRR064447','SRR064448','SRR064449','SRR064450',
		'SRR064451','SRR304656','SRR304668','SRR304683','SRR304684','SRR070081','SRR070082',
		'SRR070083','SRR070084','SRR304671','SRR304672','SRR304673','SRR304674','SRR304680']

# For MBARI
#input = ['.1-.8_coastal', '.3-20_coastal', '.8-3_coastal',
#	'.1-.8_DCM', '.3-20_DCM', '.8-3_DCM',
#	'.1-.8_surface', '.3-20_surface', '.8-3_surface',
#	'.1-.8_upwelling', '.3-20_upwelling', '.8-3_upwelling']

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



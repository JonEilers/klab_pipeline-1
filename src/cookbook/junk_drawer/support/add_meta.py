import os

home_path = os.path.dirname(os.path.realpath(__file__))
meta = home_path + '/SraAccList.tsv'
with open(meta,'r') as m:
	meta_dictionary = {}
	lines = m.readlines()
	for line in lines:
		split_line = line.strip('\n').split('\t')
		meta_dictionary[split_line[0]] = split_line[3] + '_' + split_line[2]
file = home_path + '/ETSP_ALL.fasta'
with open(file,'r') as f:
	data = f.readlines()
output = home_path + '/ETSP_ALL.prepped.fasta'
with open(output,'w') as o:
	for line in data:
			if '>' in line:
				split_line = line.split(' ')
				project_id = split_line[0].lstrip('>').replace('.', '_')
				read_id = split_line[1]
				meta_data = meta_dictionary[project_id.split('_')[0]]
				new_line = '_'.join(['>',project_id,meta_data,read_id]) + '\n'
				line = new_line
			o.write(line)
# This script is the first attempt to map domain onto each confident placement in a jplace file.
# The hope is to be able to then split the jplace file by domain to allow for directed analysis

import os
import sys
import json

HOMEPATH = os.path.dirname(os.path.realpath(__file__))
# List of commands from user
COMMANDS = sys.argv

# specify the location of the Confident_scores.csv from lineage.py
conf_lineage_file = COMMANDS[COMMANDS.index('--lineage') + 1]

#specify the location of the unknown.csv from lineage.py
#unkn_lineage_file = COMMANDS[COMMANDS.index('--unknown') + 1]

# extract read names and the domain from the confident placments lineage found
input_file_list = [conf_lineage_file]
read_name_domain = {}
for file in input_file_list:
	input = open(file,'r')
	for line in input:
		split_line = line.strip('\n').split('\t')
		if split_line[0] == 'fragment_id':
			header = split_line
		else:
			read_name = split_line[header.index('fragment_id')]
			placement_type = split_line[header.index('placement_type')]
			domain = split_line[header.index('domain_name')].replace('/','_').replace(' ','_')
			if placement_type == 'fuzzy':
					domain = 'fuzzy_' + domain.lower()
			read_name_domain[read_name] = domain
	input.close()

#specity output directory where the output jplace files
dmmd_dir = COMMANDS[COMMANDS.index('--dir-out') + 1]
parent_list = os.listdir(dmmd_dir)
if parent_list.count('dmmd') == 0:
	os.system('mkdir ' + dmmd_dir + '/dmmd')
dmmd_dir = dmmd_dir + 'dmmd/'

#jplace file being run
file = COMMANDS[COMMANDS.index('--file') + 1]
jplace_file_list = [file]

# go through each .jplace file in the directory
for jfile in jplace_file_list:
	# open file and load as a json
	jplace_data = open(jfile)
	data = json.load(jplace_data)
	jplace_data.close()
	tree = data['tree']
	placements = data['placements']
	fields = data['fields']
	# go through each placement
	for placement in placements:
		placement_index = placements.index(placement)
		reads = list(placement['p'])
		names = list(placement['nm'])
		# examine each read name
		for name_multi in names:
			name_multi_index = names.index(name_multi)
			multiplicity = str(name_multi[1])
			name = name_multi[0]
			# if the read name is also in the confident scores from lineage 
			if name in read_name_domain.keys():
				# add the confident domain to the beginning of that read name
				data['placements'][placement_index]['nm'][name_multi_index][0] = read_name_domain[name] + '.' + name
				print read_name_domain[name]
			else:
				# otherwise add "null_domain" to the beginning of that read name for filtering purposes
				data['placements'][placement_index]['nm'][name_multi_index][0] = 'NULL.' + name
				
	# resave the .jplace with the domain annotations on the confident placements
	# the files will not replace the originals but rather be named the same + .dmmd
	outjfile = dmmd_dir + jfile.split('/')[-1].rsplit('.',1)[0] + '.dmmd.jplace'
	with open(outjfile, 'w') as outfile:
  		json.dump(data, outfile, sort_keys=True, indent=1)
	print jfile, 'now has domains mapped to confident placements...'

# find all the .jplace files in the directory
#dmmd_file_list = [root + dmmdfile for root, dirs, dmmdfile in os.walk(dmmd_dir) for dmmdfile in dmmdfile if dmmdfile.split('.')[-2].find('dmmd') != -1]
# just one jfile
dmmd_file = dmmd_dir + jfile.split('/')[-1].rsplit('.',1)[0] + '.dmmd.jplace'
dmmd_file_list = [dmmd_file]

### split the new .jplace files by their domain

# find all the domains present in the mapped jplace files
domain_list = []
for dmmdfile in dmmd_file_list:
	json_data = open(dmmdfile)
	data = json.load(json_data)
	json_data.close()

	tree = data['tree']
	placements = data['placements']
	fields = data['fields']
	for placement in placements:
		reads = list(placement['p'])
		names = list(placement['nm'])
		for name in names:		
			multiplicity = str(name[1])
			name = name[0]
			for read in reads:
				domain = name.split('.')[0]
				#if domain in taxa_list or domain == 'null_domain':
				if domain not in domain_list:
					domain_list.append(domain)
print domain_list

# determine if the dmmd_split directory exists
# if not, create it
# then list the subdirectories
dmmd_parent_dir = dmmd_dir #'/'.join(dmmd_dir.split('/'))
parent_list = os.listdir(dmmd_parent_dir)
if parent_list.count('dmmd_split') == 0:
	os.system('mkdir ' + dmmd_parent_dir + '/dmmd_split')
dmmd_split_path = dmmd_parent_dir + '/dmmd_split/'

for domain in domain_list:
	split_path_list = os.listdir(dmmd_split_path)
	if domain not in split_path_list:
		os.system('mkdir ' + dmmd_split_path + domain)
	
	for dmmdfile in dmmd_file_list:
		guppy_cmd = '/home/mclaugr4/software/bin/guppy filter -Ir ' + domain
		for dom in domain_list:
			if dom != domain:
				guppy_cmd = guppy_cmd + ' -Er ' + dom
		guppy_cmd = guppy_cmd + ' ' + dmmdfile + ' -o ' + dmmd_split_path + domain + '/' + dmmdfile.split('/')[-1].rsplit('.',2)[0] + '.' + domain + '.jplace'
		print guppy_cmd
		os.system(guppy_cmd)















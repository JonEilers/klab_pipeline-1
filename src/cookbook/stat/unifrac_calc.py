import subprocess
from os import path, listdir
import sys
import json


def run_unifrac(jplace_list, out_dir, out_file):
	subprocess.Popen(' '.join([
		'guppy', 'unifrac', '--csv', '--out-dir', out_dir, ' '.join(jplace_list), '-o', out_file
		]), shell=True)

def emptyjplace(jplace_file):
	jplace_data = open(jplace_file)
	data = json.load(jplace_data)
	jplace_data.close()
	placements = data['placements']
	if not placements:
	    return False
	else:
	    return len(placements)


j_dir = sys.argv[1]
out_dir = sys.argv[2]
j_file_list = listdir(j_dir)
j_dict = {}
for j_file in j_file_list:
	full_file = path.join(j_dir, j_file)
	check_placments = emptyjplace(full_file)
	if check_placments != False:
		gene, sample = j_file.split('.')[0], j_file.split('.')[1]
		if gene in j_dict.keys():
			j_dict[gene].append(full_file)
		else:
			j_dict[gene] = [full_file]
for gene,file_list in j_dict.iteritems():
	out_file = gene + '.pmx'
	run_unifrac(file_list, out_dir, out_file)
	print gene
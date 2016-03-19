import sys
import pandas as pd
from os import listdir, path

pmx_dir = 'unifrac_out'
csv_dir = 'unifrac_csv'
file_list = listdir(pmx_dir)
for file_name in file_list:
	unifrac_table = []
	with open(path.join(pmx_dir,file_name),'r') as i:
		data = i.readlines()
		header = ['samples'] + [x for x in data[0].strip('\n').split(' ') if x != '']
		for line in data[1:]:
			split_line = [x for x in line.strip('\n').split(' ') if x != '']
			len_diff = len(header) - len(split_line)
			for i in range(len_diff):
				split_list = split_line.insert(1, '')
			unifrac_table.append(split_line)
		unifrac_df = pd.DataFrame(unifrac_table, columns=header)
		unifrac_df.to_csv(path.join(csv_dir, file_name.split('.')[0] + '.csv'), sep=',')
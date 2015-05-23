import os
import sys
import operator
import argparse
from os.path import dirname, realpath, join


# countBot.py
# Created by Ryan McLaughlin
# Last Modified 4/25/2014
# Script Function:
# This script accepts the output from the lineage.py script.
# It then outputs a .tsv which contains the number of hits of each gene in a particular taxon.
#######################################################################

def main(workdir, filelist):
	file_list = filelist.split(',')
	for file in file_list:
		countup = 0
		input = open(file, 'rU')
		geneDictionary = {}
		library_count = {}
		for line in input:
			try:
				if line.find('\t') != -1:
				        split_line = line.strip('\n').strip('\r').split('\t')
				elif line.find(',') != -1:
				        split_line = line.strip('\n').strip('\r').split(',')
				if len(split_line) > 1:
					if split_line[0] == 'origin':
						col_list = split_line
					else:
						data_list = split_line
						gene = data_list[0].split('.')[0]
						# You should make this into a flagged variable for more flexibility [Ryan 02/01/2015]
						sra_id = '_'.join(
							[data_list[col_list.index('name')].split('_')[1],
							data_list[col_list.index('name')].split('_')[0].replace('.','')]
							)
						###########################################################
						taxid = data_list[col_list.index('classification')]
						if (taxid != '10239' and taxid != '1' 
							and taxid != '131567' and taxid != '196138'):
							scientific_name = data_list[col_list.index('scientific_name')]
							domain_name = data_list[col_list.index('domain_name')]
							division_name = data_list[col_list.index('division_name')]
							class_name = data_list[col_list.index('class_name')]
							key = (gene,sra_id,scientific_name,domain_name,division_name,class_name)
							if key in geneDictionary.keys():
									geneDictionary[key] = geneDictionary[key] + 1
							else:
								geneDictionary[key] = 1
							countup = countup + 1
							Lkey = (gene,sra_id)
							if (Lkey in library_count) != False:
									library_count[Lkey] = library_count[Lkey] + 1
							else:
								library_count[Lkey] = 1
			except:
				print line
		input.close()
		print countup, file
		countup = 0
		output = open(workdir + file.split('/')[-1].split('.')[0] + '_COUNTED.tsv','w')
		output.write('\t'.join(['gene','sra_id','scientific_name','domain_name',
								'division_name','class_name','taxa_count']) + '\n')
		for key_tuple, count in geneDictionary.iteritems():
			output.write('\t'.join(key_tuple) + '\t' + str(count) + '\n')
			countup = countup + count
		output.close()
		output = open(workdir + file.split('/')[-1].split('.')[0] + '_libcount.tsv','w')
		output.write('\t'.join(['gene','taxa_count']) + '\n')
		for key_tuple, count in library_count.iteritems():
			output.write('\t'.join(key_tuple) + '\t' + str(count) + '\n')
		output.close()
		print countup


if __name__ == '__main__':
	# collect arguments from commandline
	parser = argparse.ArgumentParser(description='Welcome to CountBot! It\'s data time!')
	parser.add_argument('-w','--workdir', help='path to working directory. [default = CWD]', 
		required=False, default=dirname(realpath(__file__))
		)
	parser.add_argument('-f','--filelist', help='comma delimited list of files',
		required=True
		)
	args = vars(parser.parse_args())
	# check to make sure that enough arguments were passed before proceeding
	if len(sys.argv) < 2:
		sys.exit("Missing flags, type \"--help\" for assistance...")
	main(args['workdir'], args['filelist'])

import os
import sys
import subprocess
from os.path import dirname, realpath
import argparse

from src.code.support.DAP_DATA_PROC import jplaceDDP as DDP


def main(workdir, jdir):
	#jplace_file_list = os.listdir(jplace_path)
	jplace_file_list = []
	# If user specifies a file directory for the input .jplace files
	for root, dirs, files in os.walk(jdir, topdown=True):
		if root[-1] != '/':
			root = root + '/'
		for file in files:
			if file.split('.')[-1].find('jplace') != -1:
				# Checks to see if jplace have placements
				check_jplace = DDP(root + file).emptyjplace()
				if check_jplace != False:
					jplace_file_list.append(root + file)
				else:
					print (file, 'has no placements...')

	print (len(jplace_file_list),'files to run...')

	edpl_list = []
	for jplace in jplace_file_list:
		if jplace.split('.')[-1] == 'jplace':
			gene = jplace.split('.')[0]
			edpl_out = subprocess.check_output(['guppy', 'edpl', jplace],
							stderr = subprocess.STDOUT
							)
			out_list = edpl_out.split('\n')
			for edpl in out_list:
				if edpl.replace(' ', '') != '':
					edpl_list.append(gene + ',' 
						+ ','.join(filter(None,edpl.split(' '))))
			print (jplace, 'has been processed...')
	output = open(workdir + 'EDPL_roundup.csv', 'w')
	output.write('\n'.join(edpl_list))
	output.close()



if __name__ == '__main__':
	# collect arguments from commandline
	parser = argparse.ArgumentParser(description='Welcome to EDPL Calc! Get your jplace files ready for processing!')
	parser.add_argument('-w','--workdir', help='path to working directory. [default = CWD]', 
		required=False, default=dirname(realpath(__file__))
		)
	parser.add_argument('-d','--jdir', help='path to input jplace directory. [default = False]',
		required=False, default=False
		)
	args = vars(parser.parse_args())
	# check to make sure that enough arguments were passed before proceeding
	if len(sys.argv) < 2:
		sys.exit("Missing flags, type \"--help\" for assistance...")
	main(args['workdir'], args['jdir'])
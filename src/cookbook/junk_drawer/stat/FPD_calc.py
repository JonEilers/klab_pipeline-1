import sys
from os import listdir, system, walk
from os.path import dirname, realpath
import argparse

from src.code.support.DAP_DATA_PROC import jplaceDDP


def main(workdir, jdir):
	# Global path and directory list
	fpd_path = workdir + '/fpd/'

	# make sure fpd and rare directories exist
	parent_list = listdir(workdir)
	if parent_list.count('fpd') == 0:
		system('mkdir ' + workdir + 'fpd')

	directory_list = [jdir]
	# calculates fpd values and rarefaction curves
	for directory in directory_list:
		fileList = walk(directory)
		for root, dirs, files in fileList:
			if dirs == []:
				for file in files:
					outfile = fpd_path + file + '.fpd'
					#rareout = rare_path + file + '.rare'
					file = root + '/' + file
					if file.split('.')[-1] == 'jplace':
						# Checks to see if jplace have placements
						check_jplace = jplaceDDP(file).emptyjplace()
						if check_jplace != False:
							system('guppy fpd ' + file + ' -o ' + outfile )
						else:
							print file, 'does not have placements...'

	# collects all the fpd
	fileList = walk(fpd_path)
	output = open(workdir + 'FPD_roundup.csv','w')
	output.write('placerun,phylo_entropy,quadratic,pd,awpd\n')
	for root, dirs, files in fileList:
		for file in files:
			if file.find('.fpd') != -1:
				file = root + '/' + file
				input = open(file,'r')
				for line in input:
					if line.find('placerun') == -1:
						splitLine = line.strip('\n').split(' ')
						fpdList = []
						for v in splitLine:
							if v != '':
								fpdList.append(v)
						placerun = fpdList.pop(0)
						split_placerun = placerun.split('.')
						print file,line
						output.write(placerun + ',' + ','.join(fpdList) + '\n')

				input.close()
	output.close



if __name__ == '__main__':
	# collect arguments from commandline
	parser = argparse.ArgumentParser(description='Welcome to FPD Calc! Get your jplace files ready for processing!')
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
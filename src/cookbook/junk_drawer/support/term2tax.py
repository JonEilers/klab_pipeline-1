#! /usr/bin/env python
from re import sub
import sys
import Levenshtein
import click

# Built by Ryan McLaughlin [12/10/2014]
# Purpose is to add taxid to fasta alignent from
# standard output of phylosift.
# Taxids and names are extracted from NCBI
# Taxonomy 'names.dmp' file downloaded from
# 'ftp://ftp.ncbi.nlm.nih.gov/pub/taxonomy/'
# These names are compared to the lowest level
# names in the .fasta alignment using the pythonic
# implementation of Levenshtein ratio.
# 90% or better is considered satisfactory to be
# a match to the correct name.

def levenshtein(key_list, taxon):
	tax_key = ''
	found_name_key = 0
	for key in key_list:
		L_ratio = Levenshtein.ratio(taxon,key)
		if float(L_ratio) != float(1.0):
			if (float(L_ratio) > float(0.90) and 
				found_name_key == False
				):
				found_name_key = L_ratio
				tax_key = key
			elif float(found_name_key) < float(L_ratio):
				found_name_key = L_ratio
				tax_key = key
		else:
			found_name_key = L_ratio
			tax_key = key
			return tax_key
	return tax_key


### MAIN ###
@click.command()
@click.option('--namefile',
	help='path to NCBI Taxonomy names.dmp file.'
	)
@click.option('--infile',
	help='path to input file [.fasta].'
	)
@click.option('--outfile',
	help='path and name of output file [.fasta].'
	)
def main(namefile, infile, outfile):
	with open(namefile,'rU') as n:
		data = n.read().splitlines()
		name_list = [sub('[:;",!@$%^&.*() ]', '', 
			x.split('\t|\t')[1]) for x in data
		]
		taxid = [x.split('\t|\t')[0] for x in data]
		ncbi_name_dict = dict(zip(name_list,taxid))

	with open(infile,'rU') as i:
		fasta = i.read().splitlines()
		name_list = [x for x in fasta if x[0] == '>']
		taxa_list = [x.split(' ', 1)[1].split(';') 
			for x in fasta if x[0] == '>'
			]
		name2taxa_dict = dict(zip(name_list,taxa_list))

	with open(outfile,'w') as o:
		for line in fasta:
			if line[0] == '>':
				write_data = True
				taxa_list = name2taxa_dict[line]
				#taxid = gettax(taxa_list)
				taxon = sub('[:;",!@$%^&.*() ]', '', 
					taxa_list[-1].rsplit('.', 2)[0]
					)
				found_name_key = False
				if taxon in ncbi_name_dict.keys():
					tax_key = taxon
				else:
					tax_key = levenshtein(ncbi_name_dict.keys(),
						taxon
						)
				if tax_key == '':
					print taxon, 'has no key...'
					write_data = False
				else:
					taxid = ncbi_name_dict[tax_key]
					new_line = '>' + str(taxid) + '|' + sub(
						'[:;",!@$%^&*() ]', '|', line[1:]
						)
					o.write(new_line + '\n')
			elif write_data == True:
				o.write(line + '\n')
if __name__ == '__main__':
	if len(sys.argv) < 3 and sys.argv[1:].count('--help') == 0:
		sys.exit("Missing flags, type \"--help\" for assistance...")
	main()
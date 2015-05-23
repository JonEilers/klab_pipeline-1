import sys, os
from math import log as ln

def set_sup_path(home_path):
	'''
	make sure there is a '[CWD]/supplimentary/' directory to
	store all lineage output
	'''
	suppliment_dir_name = 'supplementary'
	if os.listdir(home_path).count(suppliment_dir_name) == 0:
		print 'The',suppliment_dir_name,'directory is required and will be created...'
		os.system('mkdir ' + home_path + '/' + suppliment_dir_name)
		supplimentary_path = home_path + '/' + suppliment_dir_name + '/' 
	else:
		supplimentary_path = home_path + '/' + suppliment_dir_name + '/'
	return supplimentary_path

def sdi(data):
    """
    >>> sdi({'x': 15, 'y': 12, 'z': 50,})
    """
    def p(n, N):
        if n is  0:
            return 0
        else:
            return (float(n)/N) * ln(float(n)/N)
            
    N = sum(data.values())
    
    return [-sum(p(n, N) for n in data.values() if n is not 0),len(data), N]

home_path = os.path.dirname(os.path.realpath(__file__))
supplimentary_path = set_sup_path(home_path)


fileList = os.listdir(supplimentary_path)

for file in fileList:
	if file.find('_COUNTED.tsv') != -1:
		output = open(supplimentary_path + file.split('.')[0] + '_SDI.csv','w')
		SDIDictionary = {}
		input = open(supplimentary_path + file)
		for line in input:
			split_line = line.strip('\n').split('\t')
			if split_line[0] == 'gene':
				header = split_line
			else:
				gene = split_line[header.index('gene')]
				sample_id = split_line[header.index('sra_id')]
				scientific_name = split_line[header.index('scientific_name')]
				domain_name = split_line[header.index('domain_name')]
				division_name = split_line[header.index('division_name')]
				class_name = split_line[header.index('class_name')]
				count = int(split_line[header.index('taxa_count')])
				key = gene + '|' + sample_id + '|' + domain_name + '|' + division_name + '|' + class_name
				tax_key = domain_name + '|' + division_name + '|' + class_name + '|' + scientific_name
				if key in SDIDictionary.keys():
					if tax_key in SDIDictionary[key].keys():
						SDIDictionary[key][tax_key] =  SDIDictionary[key][tax_key] + count
					else:
						SDIDictionary[key][tax_key] = count
				else:
					SDIDictionary[key] = {tax_key:count}
		for key, taxList in SDIDictionary.iteritems():
			split_line = key.split('|')
			gene = split_line[0]
			sample_id = split_line[1]
			domain_name = split_line[2]
			division_name = split_line[3]
			class_name = split_line[4]
			output.write(','.join(split_line) + ',' + str(sdi(taxList)[0])
					 + ',' + str(sdi(taxList)[1]) + ',' + str(sdi(taxList)[2]) + '\n'
					 ) 
		input.close()
		output.close()
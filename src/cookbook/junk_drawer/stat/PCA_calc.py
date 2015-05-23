import os

# Global path and directory list
HOMEPATH = os.path.dirname(os.path.realpath(__file__))
testdata_path = HOMEPATH + '/test_data/'
post_path = testdata_path + 'ETSP/'
pca_path = testdata_path + 'ETSP/pca/'
jplace_path = testdata_path + 'ETSP/dmmd/dmmd_split/'

# make sure pca directory exist
parent_list = os.listdir(post_path)
if parent_list.count('pca') == 0:
	os.system('mkdir ' + post_path + 'pca')

# calculates pca values
'''
gene_dictionary = {}
fileList = os.walk(jplace_path)
for root, dirs, files in fileList:
	for file in files:
		if file.split('.')[-1] == 'jplace':
			split_file = file.split('.jplace')
			gene = split_file[0].split('.')[0]
			file = root + '/' + file
			# Checks to see if jplace files have placements
			check_jplace = jplaceDDP(file).emptyjplace()
			if check_jplace != False:
				if gene in gene_dictionary.keys():
					gene_dictionary[gene].append(file)
				else:
					gene_dictionary[gene] = [file]

for gene, infiles in gene_dictionary.iteritems():
	infile = ' '.join(infiles)
	os.system('guppy pca --prefix ' + gene + ' --out-dir ' + pca_path + ' ' + infile)
'''
# collects the pca values
pca_dir = os.walk(pca_path)
output = open(post_path + 'PCA_roundup.csv','w')
output.write('gene,sample_id,domain,pca1,pca2,pca3,pca4,pca5\n')
for root, dirs, files in pca_dir:
	for file in files:
		if file.find('.trans') != -1:
			input = open(root + '/' + file, 'r')
			for line in input:
				splitLine = line.strip('\n').split(',')
				placerun = splitLine.pop(0)
				split_placerun = placerun.split('.')
				gene = split_placerun[0]
				sample_id = split_placerun[2]
				domain = split_placerun[-1]
				output.write(gene + ',' + sample_id + ',' + domain + ',' + ','.join(splitLine) + '\n')
			input.close()
output.close()
#TAXONOMY
path = './'
taxdump_path = path
work_path = path
nodes = taxdump_path + 'nodes.dmp'
'''
input = open(nodes,'r')
taxDictionary = {}
for line in input:
	split_line = line.split('\t|\t')
	taxid = int(split_line[0])
	parent_taxid = int(split_line[1])
	taxDictionary[taxid] = parent_taxid
input.close()

output = open(work_path + 'full_lineage.txt','w')
for k,v in taxDictionary.iteritems():
	full_lineage = []
	taxid = int(k)
	parent = int(v)
	full_lineage.append(str(taxid))
	if taxid == parent:
		output.write('\t'.join(full_lineage) + '\n')
	else:
		done = False
		while done == False:
			if taxDictionary.has_key(parent) == True and done == False:
				full_lineage.append(str(parent))
				taxid = parent
				parent = taxDictionary[parent]
			if taxid == parent:
				done = True
	output.write('\t'.join(full_lineage) + '\n')
output.close()
'''
input = open(work_path + 'full_lineage.txt','r')
output = open(work_path + 'update_18S_taxid_regex.txt','w')
for line in input:
	splitLine = line.strip('\n').split('\t')
	if len(splitLine) >= 3:
		if str(splitLine[-3]) == '2759':
			if len(splitLine) < 4:
				output.write('^' + splitLine[0] + '|\n')
			elif str(splitLine[-4]) != '33154':
				output.write('^' + splitLine[0] + '|\n')

output.close()
input.close()
import os
import re
import sys

s = 'gene'

# make cog to function dictionary
cog_file = '../data/ETSP_COG_SSU/cogs.csv'
with open(cog_file,'r') as c:
    cog2func = {}
    data = c.readlines()
    for index in range(0,len(data)):
        split_line = data[index].strip('\n').split(',', 2)
        cog = split_line[0]
        func_category = ','.join(list(split_line[1]))
        description = re.sub('[;,\'()\":]', '_', split_line[2]).replace(' ', '_')
        description = description.strip('_')
        cog2func[cog] = func_category, description

dir = sys.argv[1]
file_list = [x for x in os.listdir(dir) if x.find('.meta.tsv') != -1 and x.find('~') == -1]
for file_name in file_list:
    print file_name
    input = dir + '/' + file_name
    output = dir + '/' + file_name.split('.')[0] + '.funct.tsv'
    with open(input,'r') as i:
        data = i.readlines()
    with open(output,'w') as o:
        for index in range(0,len(data)):
            split_line = data[index].split('\t')
            if split_line[0] == s:
                print split_line[0]
                print file_name
                header = split_line
                split_line.insert(len(split_line)-1,'functional_category')
                split_line.insert(len(split_line)-1,'functional_description')
            else:
                gene = split_line[header.index(header[0])]
                if gene in cog2func.keys():
                    split_line.insert(len(split_line)-1, cog2func[gene][0])
                    split_line.insert(len(split_line)-1, cog2func[gene][1])
                else:
                    split_line.insert(len(split_line)-1, 'Structural_RNA')
                    split_line.insert(len(split_line)-1, 'Small_subunit_RNA')
            o.write('\t'.join(split_line))
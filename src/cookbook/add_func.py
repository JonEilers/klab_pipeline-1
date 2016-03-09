#!/usr/bin/env python

import os
import re
import sys

s = 'gene'

# make cog to function dictionary
cog_file = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../data/cogs.csv'))
with open(cog_file, 'r') as c:
    cog2func = {}
    data = c.readlines()
    for index in range(0, len(data)):
        split_line = data[index].strip('\n').split(',', 2)
        cog = split_line[0]
        func_category = ','.join(list(split_line[1]))
        description = re.sub('[;,\'()\":]', '_', split_line[2]).replace(' ', '_')
        description = description.strip('_')
        cog2func[cog] = func_category, description

dir = sys.argv[1]
file_list = [x for x in os.listdir(dir) if x.find('~') == -1 and
             x.find('placement') == -1 and os.path.isfile(os.path.join(dir, x))
             ]
for file_name in file_list:
    print file_name
    input = os.path.join(dir, file_name)
    output = os.path.join(dir, file_name.split('.')[0] + '.funct.tsv')
    with open(input, 'r') as i:
        data = i.readlines()
    with open(output, 'w') as o:
        for index in range(0, len(data)):
            split_line = data[index].split('\t')
            if split_line[0] == s:
                print split_line[0]
                print file_name
                header = split_line
                split_line.insert(len(split_line) - 1, 'functional_category')
                split_line.insert(len(split_line) - 1, 'functional_description')
            else:
                gene = split_line[header.index(header[0])]
                if gene in cog2func.keys():
                    split_line.insert(len(split_line) - 1, cog2func[gene][0])
                    split_line.insert(len(split_line) - 1, cog2func[gene][1])
                else:
                    split_line.insert(len(split_line) - 1, 'Structural_RNA')
                    split_line.insert(len(split_line) - 1, 'Small_subunit_RNA')
            o.write('\t'.join(split_line))

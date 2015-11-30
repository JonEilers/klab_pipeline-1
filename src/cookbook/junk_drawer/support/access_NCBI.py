import sys
import re

from Bio import Entrez
from Bio import Phylo


def tax2name(taxid):
    Entrez.email = "mclaugr4@students.wwu.edu"
    handle = Entrez.efetch(db='taxonomy', id=taxid, retmode='xml')
    record = Entrez.read(handle)
    handle.close()
    lineage = record[0]['Lineage']
    name = record[0]['ScientificName']
    return name


# MAIN #
file = sys.argv[1]
tree = Phylo.read(file, 'newick')
split_tree = str(tree).split('Clade')
new_split_tree = []
id2nameDict = {}
for branch in split_tree:
    if branch.find('name=') != -1:
        branch_id = branch.split(',')[1].split('\'')[1]
        taxid = branch_id.split('|')[0]
        name = re.sub('[;,():]', '_', tax2name(taxid)).replace(' ', '')
        id2nameDict[branch_id] = name + '|' + branch_id

with open(file, 'r') as R:
    data = R.readlines()
counter = 0
new_data = []
for line in data:
    for branch_id, new_branch_id in id2nameDict.iteritems():
        print new_branch_id
        try:
            line = line.replace(branch_id, new_branch_id)
        except:
            line = line
    new_data.append(line)
with open('try_it_out.tre', 'w') as t:
    t.write(''.join(new_data))

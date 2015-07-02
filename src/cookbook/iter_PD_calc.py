from Bio import Phylo
import os
import sys

tree_dir = sys.argv[1]
output_file = sys.argv[2]
tree_file_list = [root + '/' + tree for root, dirs, trees in os.walk(tree_dir)
	for tree in trees if tree.split('.')[-1].find('tre') != -1
	]
with open(output_file,'w') as o:
	o.write('gene\tgroup\ttaxid\tfaith_pd\n')
	for tree_file in tree_file_list:
		try:
			tree = Phylo.read(tree_file, 'newick')
			tree_pd = Phylo.BaseTree.TreeMixin.total_branch_length(tree)
			tree_name = tree_file.split('/')[-1].split('.')[0].split('_')
			o.write('\t'.join(tree_name) + '\t' + str(tree_pd) + '\n')
		except:
			print "Problem with tree file..."
			print tree_file

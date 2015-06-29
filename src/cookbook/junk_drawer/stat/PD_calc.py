from Bio import Phylo
import os
import sys

tree_list = [x for x in os.listdir(sys.argv[1]) if x.find('.tre') != -1]
for tree_file in tree_list:
	tree = Phylo.read(tree_file, 'newick')
	tree_pd = Phylo.BaseTree.TreeMixin.total_branch_length(tree)
	print tree_file, tree_pd
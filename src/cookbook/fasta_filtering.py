#!/usr/bin/env python

from Bio import SeqIO

from klab.process.lineage import create_taxonomy_data_structures, path_contains, _get_lineage

# 2015-05-15 ech - quick and dirty way to split out specific sub-trees from fasta files
if __name__ == '__main__':
    ncbi_dir = '../data'
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures(ncbi_dir)

    i = 0
    for seq_record in SeqIO.parse("/shared_projects/euk_fasta/18S.ref.fasta", "fasta"):
        tax_id = int(seq_record.id.split('|')[0])
        if path_contains(node_dict, tax_id, {2836}):
            # if match then write to other file
            i += 1
            print(tax_id)
            print(_get_lineage(node_dict, tax_id))
    print i

#!/usr/bin/env python

from Bio import SeqIO
import string
import sys
import os

from klab.process.lineage import create_taxonomy_data_structures, lineage_contains, get_name_from_taxa_id


# TODO ech 2015-06-29 - implement for single pass through the file instead of multiples with single keys
def filter_fasta_file(node_dict, name_dict, input_file, output_file, filter_set):
    # for big files want to not store in memory but use sequence generators to deal with single records at a time
    matching_sequences = []
    input_handle = open(input_file, 'rU')
    for record in SeqIO.parse(input_handle, 'fasta'):
        tax_id = int(record.id.split('|')[0])
        if lineage_contains(node_dict, tax_id, filter_set):
            # move id to description for safe keeping
            record.description = record.id
            # replace id for better tree visualization
            record.id = str(tax_id) + '|' + string.replace(name_dict.get(tax_id), ' ', '_')
            matching_sequences.append(record)
    input_handle.close()
    output_handle = open(output_file, 'w')
    SeqIO.write(matching_sequences, output_handle, "fasta")
    output_handle.close()
    print "Wrote %i matching sequences to %s" % (len(matching_sequences), output_file)


if __name__ == '__main__':
    # first argument is full path to directory where ncbi data files live
    # second argument is full path to fasta file you want to split
    # TODO - third arguemt is file that contains taxon_id, include/exclude, optional_name

    ncbi_dir = sys.argv[1]
    nodes, names, merged, deleted = create_taxonomy_data_structures(ncbi_dir)

    file_path = sys.argv[2]
    new_dir = file_path.split('.')[0]
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    groups = {2830, 2836, 3041, 2864, 3027}  # TODO ech 2015-06-29 - migrate this to file
    for group_id in groups:
        group_name = string.lower(get_name_from_taxa_id(group_id, names, deleted))
        filter_fasta_file(nodes, names, file_path, os.path.join(new_dir, group_name + '_' + str(group_id) + '.fasta'),
                          {group_id})

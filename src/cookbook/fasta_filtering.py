#!/usr/bin/env python

from Bio import SeqIO

from klab.process.lineage import create_taxonomy_data_structures, lineage_contains

# 2015-05-15 ech - quick and dirty way to split out specific sub-trees from fasta files
if __name__ == '__main__':
    ncbi_dir = '../data'
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures(ncbi_dir)

    # for big files want to not store in memory but use sequence generators to deal with single records at a time
    matching_sequences = []
    input_handle = open('/shared_projects/euk_fasta/18S.ref.fasta', 'rU')
    for record in SeqIO.parse(input_handle, 'fasta'):
        tax_id = int(record.id.split('|')[0])
        if lineage_contains(node_dict, tax_id, {2836, 2830}):
            matching_sequences.append(record)
    input_handle.close()

    print "Found %i matching sequences" % len(matching_sequences)

    output_handle = open('/shared_projects/euk_fasta/output.fasta', 'w')
    SeqIO.write(matching_sequences, output_handle, "fasta")
    output_handle.close()

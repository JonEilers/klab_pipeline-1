#!/usr/bin/env python

from Bio import SeqIO
import string

from klab.process.lineage import create_taxonomy_data_structures, lineage_contains


def filter_fasta_file(node_dict, name_dict, input_file, output_file, filter_set):
    # for big files want to not store in memory but use sequence generators to deal with single records at a time
    matching_sequences = []
    input_handle = open(input_file, 'rU')
    for record in SeqIO.parse(input_handle, 'fasta'):
        tax_id = int(record.id.split('|')[0])
        if lineage_contains(node_dict, tax_id, filter_set):
            # replace id and description for easier visualization
            record.id = str(tax_id) + '|' + string.replace(name_dict.get(tax_id), ' ', '_')
            record.description = ''
            matching_sequences.append(record)
    input_handle.close()

    print "Wrote %i matching sequences to %s" % (len(matching_sequences), output_file)

    output_handle = open(output_file, 'w')
    SeqIO.write(matching_sequences, output_handle, "fasta")
    output_handle.close()


# 2015-05-15 ech - quick and dirty way to split out specific sub-trees from fasta files
if __name__ == '__main__':
    ncbi_dir = '../data'
    nodes, names, merged, deleted = create_taxonomy_data_structures(ncbi_dir)

    dir = '/shared_projects/euk_fasta/'
    filter_fasta_file(nodes, names, dir + '18S.ref.fasta', dir + 'haptophyes.fasta', {2830})
    filter_fasta_file(nodes, names, dir + '18S.ref.fasta', dir + 'diatoms.fasta', {2836})
    filter_fasta_file(nodes, names, dir + '18S.ref.fasta', dir + 'greens.fasta', {3041})
    filter_fasta_file(nodes, names, dir + '18S.ref.fasta', dir + 'dinos.fasta', {2864})
    filter_fasta_file(nodes, names, dir + '18S.ref.fasta', dir + 'cryptophytes.fasta', {3027})

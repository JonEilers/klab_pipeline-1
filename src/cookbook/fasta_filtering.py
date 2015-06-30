#!/usr/bin/env python

from Bio import SeqIO
import re
import string
import sys
import os

from klab.process.lineage import create_taxonomy_data_structures, get_lineage, get_name_from_taxa_id


def _lineage_contains(lineage, match_set):
    intersection = list(set(lineage) & match_set)
    return len(intersection) > 0


# TODO ech 2015-6-30 - this might be useful elsewhere as a utility
def _turn_ncbi_name_into_file_name(ncbi_name):
    s = string.lower(ncbi_name).strip()  # lower case and trim leading/trailing spaces, if any
    s = re.sub(r'[ /)(&\.]+', '_', s)  # replace whacky characters with underscore and shrink multiples
    s = re.sub(r'_$', '', s)  # drop trailing underscore, if any
    return s


def filter_fasta_file(node_dict, name_dict, input_file, output_file, include, exclude):
    # for big files want to not store in memory but use sequence generators to deal with single records at a time
    matching_sequences = []
    input_handle = open(input_file, 'rU')
    for record in SeqIO.parse(input_handle, 'fasta'):
        tax_id = int(record.id.split('|')[0])
        lineage = get_lineage(node_dict, tax_id)
        if _lineage_contains(lineage, include):
            # check for non-empty exclude set avoids unnecessary lineage check
            if not exclude or not _lineage_contains(lineage, exclude):
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


def _split_fasta_file(ncbi_dir, input_file, output_dir, include_set, exclude_set):
    if not os.path.isdir(ncbi_dir):
        raise ValueError(ncbi_dir + ' is not a directory.')
    if not os.path.isfile(input_file):
        raise ValueError(input_file + ' is not a file.')

    nodes, names, merged, deleted = create_taxonomy_data_structures(ncbi_dir)

    cluster = os.path.basename(input_file).split('.')[0]  # pull first part of filename (ex: 'COG0001')
    new_dir = os.path.join(output_dir, cluster)
    if not os.path.exists(new_dir):
        os.makedirs(new_dir)

    for group_id in include_set:
        # don't need exhaustively long names, so trim it at 15
        group_name = _turn_ncbi_name_into_file_name(get_name_from_taxa_id(group_id, names, deleted))[:15]
        out = cluster + '_' + group_name + '_' + str(group_id) + '.fasta'
        filter_fasta_file(nodes, names, input_file, os.path.join(new_dir, out), {group_id}, exclude_set)


if __name__ == '__main__':
    # first argument is full path to directory where ncbi data files live
    # second argument is full path to fasta file you want to split
    # third argument is output directory
    ncbi_dir = sys.argv[1]
    input_file = sys.argv[2]
    output_dir = sys.argv[3]

    # TODO - fourth argument is file that contains tax_id, include/exclude, optional_name
    include_set = {2830, 2836, 3041, 2864, 3027}  # TODO ech 2015-06-29 - migrate these two items to file
    exclude_set = set()  # {2831}  # test value

    _split_fasta_file(ncbi_dir, input_file, output_dir, include_set, exclude_set)

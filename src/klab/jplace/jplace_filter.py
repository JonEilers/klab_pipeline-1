#!/usr/bin/env python

from __future__ import unicode_literals

import argparse
import os

import numpy

from klab.process.file_manager import get_files, get_json_contents
from klab.process.lineage import create_taxonomy_data_structures, get_lineage

try:
    import simplejson as json
except ImportError:  # pragma nocover
    import json  # simplejson has better feedback on parsing failures


def transpose_name_dict(name_dict):
    tnd = {}
    for k, v in name_dict.items():
        tnd[v.lower()] = k
    return tnd


def filter_jplace_files(files, output_dir, filter_items, node_dict=None, name_dict=None):
    if not node_dict:  # way for tests to inject the information
        node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures()  # pragma nocover
    t_name_dict = transpose_name_dict(name_dict)

    filter_taxa = []
    for i in filter_items:
        try:
            item = int(i)
            if item in name_dict:
                filter_taxa.append(item)
            else:
                raise RuntimeError('%d is not a NCBI taxa id' % item)
        except ValueError:
            if i.lower() in t_name_dict:
                filter_taxa.append(t_name_dict[i.lower()])
            else:
                raise RuntimeError('"%s" is not a NCBI taxa name' % i)

    for path in files:
        contents = get_json_contents(path)
        if contents and contents['placements'] != []:
            file_name = os.path.basename(path)
            classification_index = contents['fields'].index('classification')  # find the taxa_id column
            filtered_items = []
            items = contents['placements']
            for item in items:
                taxa_id = int(item['p'][0][classification_index])  # pull the best placement[0] taxa_id
                lineage, rank = get_lineage(node_dict, taxa_id)
                # if nothing in the lineage matches anything in the filter list then keep it
                if len(numpy.intersect1d(lineage, filter_taxa, assume_unique=True)) == 0:
                    filtered_items.append(item)
            if len(filtered_items) == 0:
                print('Removed all placements from %s. Not creating empty copy.' % file_name)  # pragma nocover
            else:
                if len(items) == len(filtered_items):
                    print('%s is unchanged' % file_name)  # pragma nocover
                else:
                    print('Removed %d of %d placements from %s' %
                          (len(items) - len(filtered_items), len(items), file_name))  # pragma nocover
                    contents['placements'] = filtered_items
                with open(os.path.join(output_dir, file_name), 'w') as outfile:
                    json.dump(contents, outfile, indent=1, separators=(',', ':'))


if __name__ == '__main__':  # pragma nocover
    parser = argparse.ArgumentParser(description='Remove certain placements from jplace files.')
    parser.add_argument('-directory', help='directory with original jplace files', required=True)
    parser.add_argument('-taxa', help='quote-enclosed comma-separated list of undesired NCBI taxa names or ids'
                                      ' ex: "Bacteria,10239" (id for Viruses superkingdom)',
                        required=True)
    parser.add_argument('-out_dir', help='output directory for filtered jplace files', required=True)
    args = parser.parse_args()

    out_dir = os.path.abspath(args.out_dir)
    if not os.path.isdir(out_dir):
        raise IOError('Output directory "%s" does not exist.' % out_dir)

    in_dir = os.path.abspath(args.directory)
    if not os.path.isdir(in_dir):
        raise IOError('Input directory "%s" does not exist.' % in_dir)

    jplace_files = get_files(in_dir)
    if not jplace_files:
        raise IOError('No jplace files were found under directory %s' % in_dir)

    t = [x.strip() for x in args.taxa.split(',')]

    filter_jplace_files(files=jplace_files, output_dir=args.out_dir, filter_items=t)

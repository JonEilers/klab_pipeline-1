#!/usr/bin/env python

import argparse
import os
import subprocess

import pandas as pd

from klab.process.file_manager import read_df_from_file, write_df_to_file, CLASSIFICATION_COLUMN

ROOT_ID = 1
CELLULAR_ORGANISMS_ID = 131567
VIRUS_ID = 10239

MISSING_ID = -1
MISSING_ID_LIST = [MISSING_ID] * 4
NO_MATCH = 'NO MATCH'
NO_NAME = 'MISSING NAME'
DELETED_NAME = 'DELETED NODE'


def _build_dict_from_file(node_file):
    d = {}
    f = open(node_file, 'r')
    try:
        for row in f:
            columns = row.split('\t')
            key = int(columns[0])
            v = columns[1].rstrip()
            try:
                value = int(v)  # might be an int, might be a string
            except ValueError:
                value = v
            d[key] = value
    finally:
        f.close()
    return d


def _build_deleted_list(delnode_file):
    l = []
    f = open(delnode_file, 'r')
    try:
        for row in f:
            id = int(row.rstrip())
            l.append(id)
    finally:
        f.close()
    return l


def _get_specific_taxonomy_levels(taxonomy_list):
    if not taxonomy_list:
        return MISSING_ID_LIST

    most_specific_id = taxonomy_list[-1:]  # create a list with last element
    padded_list = list(taxonomy_list) + MISSING_ID_LIST  # copy taxa list and pad with missing ids
    domain_division_class_ids = padded_list[:3]  # get first three in list (may include missing ids)
    return domain_division_class_ids + most_specific_id


def get_lineage(node_dict, leaf):
    parent_id = node_dict.get(leaf)
    lineage = [leaf]
    while parent_id and parent_id != CELLULAR_ORGANISMS_ID and parent_id != ROOT_ID:
        lineage.append(parent_id)
        parent_id = node_dict.get(parent_id)
    return lineage[::-1]  # reverse the order so it starts with highest node


def build_lineage_matrix(node_dict, placements, full_taxa=False):
    leaf_list = placements[CLASSIFICATION_COLUMN].unique()  # only build lineage for this set of placements
    lineage_matrix = []
    for leaf in leaf_list:
        lineage = get_lineage(node_dict, leaf)
        depth = len(lineage)
        if full_taxa:
            lineage_matrix.append(lineage)
        else:
            upper_taxa = _get_specific_taxonomy_levels(lineage)
            lineage_matrix.append([depth] + upper_taxa)
    return lineage_matrix


def _build_lineage_frame(node_dict, placements):
    lineage_matrix = build_lineage_matrix(node_dict, placements, False)
    df = pd.DataFrame(data=lineage_matrix,
                      columns=['taxa_depth', 'domain_id', 'division_id', 'class_id', CLASSIFICATION_COLUMN])
    return df


def get_name_from_taxa_id(tid, name_dict, deleted_list):
    val = name_dict.get(tid, NO_NAME)
    if val == NO_NAME and tid in deleted_list:
        val = DELETED_NAME
    return val


def add_name_column(df, id_column, name_column, name_dict, deleted_list):
    df[name_column] = df[id_column].apply(get_name_from_taxa_id, args=(name_dict, deleted_list))
    return df


def create_taxonomy_data_structures():
    ncbi_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data'))
    return_code = subprocess.call(os.path.join(ncbi_dir, 'get_ncbi_data.sh'), shell=True)
    if return_code != 0:
        raise Exception('Problem getting NCBI data.')
    node_dict = _build_dict_from_file(os.path.join(ncbi_dir, 'nodes.tsv'))
    name_dict = _build_dict_from_file(os.path.join(ncbi_dir, 'names.tsv'))
    name_dict[MISSING_ID] = NO_MATCH  # better to add here than make a special case in code
    merged_dict = _build_dict_from_file(os.path.join(ncbi_dir, 'merged.tsv'))
    deleted_list = _build_deleted_list(os.path.join(ncbi_dir, 'delnodes.tsv'))
    return node_dict, name_dict, merged_dict, deleted_list


# update old ids with new ones (if they exist) otherwise keep existing
def _update_classification_ids(df, merged_dict):
    df[CLASSIFICATION_COLUMN] = df[CLASSIFICATION_COLUMN].apply(lambda x: merged_dict.get(x, x))
    return df


def create_lineage(placements, out_file=None):
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures()
    placements = _update_classification_ids(placements, merged_dict)
    lineage_frame = _build_lineage_frame(node_dict=node_dict, placements=placements)
    add_name_column(lineage_frame, 'domain_id', 'domain_name', name_dict, deleted_list)
    add_name_column(lineage_frame, 'division_id', 'division_name', name_dict, deleted_list)
    add_name_column(lineage_frame, 'class_id', 'class_name', name_dict, deleted_list)
    add_name_column(lineage_frame, CLASSIFICATION_COLUMN, 'lowest_classification_name', name_dict, deleted_list)

    df = pd.merge(left=placements, right=lineage_frame, on=CLASSIFICATION_COLUMN, how='left')
    if out_file:
        write_df_to_file(df, out_file)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-placement_file', help='sequence placement file', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    p = read_df_from_file(args.placement_file)
    create_lineage(placements=p, out_file=args.out_file)

    # -p '/placeholder/test/data/test_placements.tsv' -o '/placeholder/test/data/test_placements_with_lineage.tsv'
    # -p '/shared_data/2014_placements.tsv' -o '/shared_data/2014_placements_with_lineage.tsv'
    # -p '/shared_data/2012_placements.tsv' -o '/shared_data/2012_placements_with_lineage.tsv'

#!/usr/bin/env python

import argparse
import os
import subprocess

import pandas as pd

from klab.process.derived_info import add_placement_type_column
from klab.process.file_manager import read_df_from_file, write_df_to_file, CLASSIFICATION_COLUMN

ROOT_ID = 1
CELLULAR_ORGANISMS_ID = 131567
VIRUS_ID = 10239

MISSING_ID = -1
MISSING_ID_LIST = [MISSING_ID] * 20
NO_MATCH = 'NO MATCH'
NO_NAME = 'MISSING NAME'
DELETED_NAME = 'DELETED NODE'
NO_RANK = 'no rank'


def _build_merged_dict(merged_file):
    d = {}
    f = open(merged_file, 'r')
    try:
        for row in f:
            columns = row.split('\t')
            key = int(columns[0])
            d[key] = int(columns[1].rstrip())
    finally:
        f.close()
    return d


def _build_names_dict(names_file):
    d = {}
    f = open(names_file, 'r')
    try:
        for row in f:
            columns = row.split('\t')
            key = int(columns[0])
            d[key] = columns[1].rstrip()
    finally:
        f.close()
    return d


def _build_node_dict(node_file):
    d = {}
    f = open(node_file, 'r')
    try:
        for row in f:
            columns = row.split('\t')
            key = int(columns[0])
            d[key] = (int(columns[1].rstrip()), columns[2].rstrip())
    finally:
        f.close()
    return d


def _build_deleted_list(delnode_file):
    l = []
    f = open(delnode_file, 'r')
    try:
        for row in f:
            taxa = int(row.rstrip())
            l.append(taxa)
    finally:
        f.close()
    return l


# Get a list of specific matches to taxa names ('superkingdom','phylum','class', etc)
# WARNING: there are a lot of 'no rank' taxa in ncbi lineages - a given level might have spotty coverage
def _get_specific_taxonomy_levels(taxonomy_list, lineage, rank):
    if not lineage:
        return MISSING_ID_LIST[:len(taxonomy_list) + 1]

    res = []
    for t in taxonomy_list:
        try:
            i = rank.index(t)
            res.append(lineage[i])
        except ValueError:
            res.append(MISSING_ID)
    res.append(lineage[-1])  # append lowest taxa item in every case
    return res


# This is the way we mostly do it - take the first three taxa levels ('domain','division','errr...") and the lowest
def _get_top_three_and_lowest_levels(lineage):
    if not lineage:
        return MISSING_ID_LIST[:4]

    most_specific_id = lineage[-1:]  # create a list with last element
    padded_list = list(lineage) + MISSING_ID_LIST  # copy taxa list and pad with missing ids
    top_three = padded_list[:3]  # get first three in list (may include missing ids)
    return top_three + most_specific_id


def get_lineage(node_dict, leaf):
    lineage = [leaf]
    if leaf not in node_dict:
        return lineage, [NO_RANK]

    parent_id, r = node_dict.get(leaf)
    rank = [r]
    while parent_id and parent_id != CELLULAR_ORGANISMS_ID and parent_id != ROOT_ID:
        lineage.append(parent_id)
        parent_id, r = node_dict.get(parent_id)
        rank.append(r)
    return lineage[::-1], rank[::-1]  # reverse the order so they start with highest node


def build_lineage_matrix(node_dict, placements, taxa_list=(), full_taxa=False):
    leaf_list = placements[CLASSIFICATION_COLUMN].unique()  # only build lineage for this set of placements
    lineage_matrix = []
    for leaf in leaf_list:
        lineage, rank = get_lineage(node_dict, leaf)
        depth = len(lineage)
        if full_taxa:
            lineage_matrix.append(lineage)
        else:
            if taxa_list:
                taxa = _get_specific_taxonomy_levels(taxa_list, lineage, rank)
            else:
                taxa = _get_top_three_and_lowest_levels(lineage)
            lineage_matrix.append([depth] + taxa)
    return lineage_matrix


def _build_lineage_frame(node_dict, placements, taxa_list=()):
    lineage_matrix = build_lineage_matrix(node_dict, placements, taxa_list=taxa_list, full_taxa=False)
    if taxa_list:
        col = ['taxa_depth']
        col.extend(['%s_id' % t for t in taxa_list])
        col.append(CLASSIFICATION_COLUMN)
        df = pd.DataFrame(data=lineage_matrix, columns=col)
    else:
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
    node_dict = _build_node_dict(os.path.join(ncbi_dir, 'nodes.tsv'))
    name_dict = _build_names_dict(os.path.join(ncbi_dir, 'names.tsv'))
    name_dict[MISSING_ID] = NO_MATCH  # better to add here than make a special case in code
    merged_dict = _build_merged_dict(os.path.join(ncbi_dir, 'merged.tsv'))
    deleted_list = _build_deleted_list(os.path.join(ncbi_dir, 'delnodes.tsv'))
    return node_dict, name_dict, merged_dict, deleted_list


# update old ids with new ones (if they exist) otherwise keep existing
def _update_classification_ids(df, merged_dict):
    df[CLASSIFICATION_COLUMN] = df[CLASSIFICATION_COLUMN].apply(lambda x: merged_dict.get(x, x))
    return df


def create_lineage(placements, taxa_list=(), out_file=None):
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures()
    placements = _update_classification_ids(placements, merged_dict)
    lineage_frame = _build_lineage_frame(node_dict=node_dict, placements=placements, taxa_list=taxa_list)
    # write_df_to_file(lineage_frame, '~/Desktop/lineage.tsv')  # TODO ech 2016-11-17 - remove this after testing
    if taxa_list:
        for t in taxa_list:
            add_name_column(lineage_frame, '%s_id' % t, '%s_name' % t, name_dict, deleted_list)
    else:
        add_name_column(lineage_frame, 'domain_id', 'domain_name', name_dict, deleted_list)
        add_name_column(lineage_frame, 'division_id', 'division_name', name_dict, deleted_list)
        add_name_column(lineage_frame, 'class_id', 'class_name', name_dict, deleted_list)
    add_name_column(lineage_frame, CLASSIFICATION_COLUMN, 'lowest_classification_name', name_dict, deleted_list)

    df = pd.merge(left=placements, right=lineage_frame, on=CLASSIFICATION_COLUMN, how='left')
    add_placement_type_column(df)
    if out_file:
        write_df_to_file(df, out_file)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-placement_file', help='sequence placement file', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    p = read_df_from_file(args.placement_file)
    create_lineage(placements=p, out_file=args.out_file, taxa_list=['superkingdom', 'phylum', 'class'])

    # -p '/placeholder/test/data/test_placements.tsv' -o '/placeholder/test/data/test_placements_with_lineage.tsv'
    # -p '/shared_data/2014_placements.tsv' -o '/shared_data/2014_placements_with_lineage.tsv'
    # -p '/shared_data/2012_placements.tsv' -o '/shared_data/2012_placements_with_lineage.tsv'

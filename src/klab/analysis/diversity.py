#!/usr/bin/env python

from __future__ import division

import argparse
import os

import pandas as pd
import numpy as np

from klab.process.derived_info import group_and_count
from klab.process.file_manager import write_df_to_file, create_placements, CLASSIFICATION_COLUMN
from klab.process.lineage import build_lineage_matrix, create_taxonomy_data_structures, add_name_column

CLASSIFICATION_NAME_COLUMN = 'classification_name'
NORMALIZE_COLUMN = 'normalize_factor'


def _calculate_similarity(lineage_dict, a, b):
    if a == b:
        return 1

    long_lineage = lineage_dict.get(a, [])
    short_lineage = lineage_dict.get(b, [])
    if len(short_lineage) > len(long_lineage):
        t = short_lineage
        short_lineage = long_lineage
        long_lineage = t

    if len(long_lineage) == 0:
        return 0

    matches = 0
    for i in range(len(short_lineage)):
        if short_lineage[i] == long_lineage[i]:
            matches += 1
        else:
            break
    return matches / len(long_lineage)


def _build_lineage_dict(node_dict, abundance):
    lm = build_lineage_matrix(node_dict, abundance, full_taxa=True)
    ld = {}
    for r in lm:
        ld[r[-1]] = r
    return ld


def _build_similarity_matrix(node_dict, abundance):
    ld = _build_lineage_dict(node_dict, abundance)
    taxa_id_list = list(abundance[CLASSIFICATION_COLUMN])
    d = len(taxa_id_list)
    sm = np.zeros((d, d))
    for i in range(d):
        sm[i][i] = 1
        for j in range(i):
            sim = _calculate_similarity(ld, taxa_id_list[i], taxa_id_list[j])
            sm[i][j] = sim
            sm[j][i] = sim
    return sm, taxa_id_list,


def _normalize_data(compare_column, placements):
    if NORMALIZE_COLUMN not in placements.columns:
        return placements

    # group the placements - assume ungrouped and has a 'normalize_factor' column
    c = group_and_count(placements,
                        [CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, compare_column, NORMALIZE_COLUMN])
    # calculate the normalized counts
    c['norm_count'] = c[NORMALIZE_COLUMN] * c['count']
    c.drop([NORMALIZE_COLUMN, 'count'], axis=1, inplace=True)
    return c


# filter and pivot the dataframe by compare_column, then calculate abundance and similarity
def create_n_way_diversity_files(node_dict, placements, compare_column, path):
    c = _normalize_data(compare_column, placements)

    # group and sum up the counts
    n = c.groupby([CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, compare_column]).sum().reset_index()

    # pivot and unstack to break out values by compare column
    t = pd.pivot_table(n, index=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, compare_column], aggfunc=[np.sum])
    abundance = t.unstack()
    abundance.fillna(0, inplace=True)

    # clean up and flatten the multi-index
    abundance.columns = abundance.columns.get_level_values(2)
    abundance.reset_index(inplace=True)

    write_df_to_file(abundance, path + 'abundance.tsv')

    # make and save the similarity matrix
    similarity = build_similarity_frame(node_dict, abundance)
    write_df_to_file(similarity, path + 'similarity.tsv')


def build_similarity_frame(node_dict, abundance):
    sm, k = _build_similarity_matrix(node_dict, abundance)
    df = pd.DataFrame(data=sm, columns=abundance[CLASSIFICATION_NAME_COLUMN])
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='directory with .jplace files', required=True)
    parser.add_argument('-out_directory', help='output directory', required=True)
    args = parser.parse_args()

    # little hacky to use relative path from this file
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data')

    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures(data_dir)
    placements = create_placements(args.directory)
    add_name_column(placements, CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, name_dict, deleted_list)

    abundance = group_and_count(placements, [CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN])
    write_df_to_file(abundance, os.path.join(args.out_directory, 'abundance.tsv'))

    similarity = build_similarity_frame(node_dict, abundance)
    write_df_to_file(similarity, os.path.join(args.out_directory, 'similarity_matrix.tsv'))

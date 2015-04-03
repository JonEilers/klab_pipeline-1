#!/usr/bin/env python

from __future__ import division

import numpy as np
import pandas as pd

from klab.process.derived_info import group_and_count
from klab.process.file_manager import write_df_to_file, create_placements, CLASSIFICATION_COLUMN
from klab.process.lineage import build_lineage_matrix, create_taxonomy_data_structures, add_name_column


CLASSIFICATION_NAME_COLUMN = 'classification_name'


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
            similarity = _calculate_similarity(ld, taxa_id_list[i], taxa_id_list[j])
            sm[i][j] = similarity
            sm[j][i] = similarity
    return sm, taxa_id_list,


def build_similarity_frame(node_dict, abundance):
    sm, k = _build_similarity_matrix(node_dict, abundance)
    df = pd.DataFrame(data=sm, columns=abundance[CLASSIFICATION_NAME_COLUMN])
    return df


if __name__ == '__main__':
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures('/package_compare/src/ncbi_data')
    placements = create_placements('/shared_projects/seastar/data/bm_ssu_analysis')
    add_name_column(placements, CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, name_dict, deleted_list)

    abundance = group_and_count(placements, [CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN])
    write_df_to_file(abundance, '/package_compare/test/diversity/abundance.tsv')

    similarity = build_similarity_frame(node_dict, abundance)
    write_df_to_file(similarity, '/package_compare/test/diversity/similarity_matrix.tsv')

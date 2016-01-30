#!/usr/bin/env python
import os

import pandas as pd
import numpy as np

from klab.process.file_manager import read_df_from_file, write_df_to_file, CLASSIFICATION_COLUMN
from klab.process.derived_info import group_and_count
from klab.process.lineage import create_taxonomy_data_structures
from klab.analysis.diversity import build_similarity_frame, CLASSIFICATION_NAME_COLUMN


def _normalize_data(compare_column, placements):
    if 'normalize_factor' not in placements.columns:
        return placements

    # group the placements - assume ungrouped and has a 'normalize_factor' column
    c = group_and_count(placements,
                        [CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, compare_column, 'normalize_factor'])
    # calculate the normalized counts
    c['norm_count'] = c['normalize_factor'] * c['count']
    c.drop(['normalize_factor', 'count'], axis=1, inplace=True)
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


if __name__ == '__main__':
    # load up the ncbi data
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data')
    node_dict, name_dict, merged_dict, deleted_list = create_taxonomy_data_structures(data_dir)

    # get the file with all the data and rename one of the columns
    seastar_dir = '/Users/ehervol/Dropbox/shared_projects/seastar/'
    placements = read_df_from_file(seastar_dir + 'BM_refpkg_ssu_whole_enchilada.tsv')
    placements.rename(columns={'lowest_classification_name': CLASSIFICATION_NAME_COLUMN}, inplace=True)
    # only take confident placements
    p = placements[placements.placement_type == 'confident']

    create_n_way_diversity_files(node_dict, p, 'host_disease', seastar_dir + 'bm_ssu_disease_confident_')
    create_n_way_diversity_files(node_dict, p, 'host', seastar_dir + 'bm_ssu_species_confident_')
    create_n_way_diversity_files(node_dict, p, 'library_name', seastar_dir + 'bm_ssu_library_confident_')
    create_n_way_diversity_files(node_dict, p, 'location', seastar_dir + 'bm_ssu_location_confident_')

    p2 = p[p.host_disease == 'Asymptomatic']
    create_n_way_diversity_files(node_dict, p2, 'host', seastar_dir + 'bm_ssu_asymptomatic_species_confident_')
    p2 = p[p.host_disease == 'Symptomatic']
    create_n_way_diversity_files(node_dict, p2, 'host', seastar_dir + 'bm_ssu_symptomatic_species_confident_')

#!/usr/bin/env python
import os

from klab.process.file_manager import read_df_from_file
from klab.process.lineage import create_taxonomy_data_structures
from klab.analysis.diversity import CLASSIFICATION_NAME_COLUMN, create_n_way_diversity_files

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

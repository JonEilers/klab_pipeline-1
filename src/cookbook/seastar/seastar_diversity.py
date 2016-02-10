#!/usr/bin/env python
import os

from klab.process.derived_info import CONFIDENT
from klab.process.file_manager import read_df_from_file
from klab.analysis.diversity import CLASSIFICATION_NAME_COLUMN, create_n_way_diversity_files

if __name__ == '__main__':
    # get the file with all the data and rename one of the columns
    seastar_dir = '/Users/ehervol/Dropbox/shared_projects/seastar'
    placements = read_df_from_file(os.path.join(seastar_dir, 'BM_refpkg_ssu_whole_enchilada.tsv'))
    placements.rename(columns={'lowest_classification_name': CLASSIFICATION_NAME_COLUMN}, inplace=True)

    # only take confident placements
    p = placements[placements.placement_type == CONFIDENT]

    create_n_way_diversity_files(p, 'host_disease', os.path.join(seastar_dir, 'host_disease'))
    # create_n_way_diversity_files(p, 'host', os.path.join(seastar_dir, 'bm_ssu_species_confident'))
    # create_n_way_diversity_files(p, 'library_name', os.path.join(seastar_dir, 'bm_ssu_library_confident'))
    # create_n_way_diversity_files(p, 'location', os.path.join(seastar_dir, 'bm_ssu_location_confident'))

    # p2 = p[p.host_disease == 'Asymptomatic']
    # create_n_way_diversity_files(p2, 'host', os.path.join(seastar_dir, 'bm_ssu_asymptomatic_species_confident'))
    # p2 = p[p.host_disease == 'Symptomatic']
    # create_n_way_diversity_files(p2, 'host', os.path.join(seastar_dir, 'bm_ssu_symptomatic_species_confident'))

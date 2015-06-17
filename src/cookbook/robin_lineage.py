#!/usr/bin/env python

#########################
# Robin specific requests
#########################

from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
from klab.process.file_manager import write_df_to_file, create_placements
from cookbook.mbari_lineage import create_mbari_lineage_files
from klab.process.lineage import create_lineage


def create_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def create_mbari_files_for_robin(base):
    l = create_mbari_lineage_files(base)
    create_count_files(l, ['cluster', 'domain_name', 'size', 'location', 'placement_type'], base + 'domain_')
    create_count_files(l, ['cluster', 'domain_name', 'division_name', 'size', 'location', 'placement_type'],
                       base + 'division_')
    create_count_files(l, ['cluster', 'domain_name', 'division_name', 'lowest_classification_name', 'size', 'location',
                           'placement_type'], base + 'classification_')


def create_wdfw_placement_files_for_robin(base):
    p = create_placements(dir=base)
    path = base + 'wdfw'
    l = create_lineage(ncbi_dir='/placeholder/src/data', placements=p,
                       out_file=path + '_placements_with_lineage.tsv')
    create_count_files(l, ['domain_name', 'placement_type'], path + '_domain_')
    create_count_files(l, ['domain_name', 'division_name', 'placement_type'], path + '_division_')
    create_count_files(l, ['domain_name', 'division_name', 'lowest_classification_name', 'placement_type'],
                       path + '_classification_')


if __name__ == '__main__':
    create_wdfw_placement_files_for_robin('/data/wdfw/')

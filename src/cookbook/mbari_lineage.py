#!/usr/bin/env python

from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
from klab.process.file_manager import create_placements, write_df_to_file
from klab.process.lineage import create_lineage

from cookbook.mbari import add_mbari_size_column, add_mbari_location_column


def create_lineage_files(base):
    jplace_dir = base + 'analysis'
    lineage_file = base + 'placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    l = create_lineage(ncbi_dir='/package_compare/src/ncbi_data', placements=p)
    add_mbari_size_column(l)
    add_mbari_location_column(l)
    write_df_to_file(l, lineage_file)
    return l


def create_and_write_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def do_the_do(base):
    l = create_lineage_files(base)

    create_and_write_count_files(l, ['cluster', 'domain_name', 'size', 'location', 'placement_type'], base + 'domain_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'size', 'location', 'placement_type'],
                                 base + 'division_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'lowest_classification_name', 'size',
                                     'location', 'placement_type'], base + 'classification_')


# ech 2015-03-07 - take the repetition out of rebuilding the mbari data
if __name__ == '__main__':
    # do_the_do('/data/2014_MBARI_ssu_')
    # do_the_do('/data/2014_MBARI_cluster_')
    # do_the_do('/data/2014_MBARI_tigr_')
    do_the_do('/data/2014_MBARI_cog_')


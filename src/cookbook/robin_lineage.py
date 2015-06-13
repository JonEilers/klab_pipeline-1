#!/usr/bin/env python

from os import walk

from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
from klab.process.file_manager import write_df_to_file, read_df_from_file, create_placements
from cookbook.mbari_lineage import create_mbari_lineage_files
from klab.process.lineage import create_lineage

# Robin specific requests

def create_and_write_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def create_mbari_files_for_robin(base):
    l = create_mbari_lineage_files(base)

    create_and_write_count_files(l, ['cluster', 'domain_name', 'size', 'location', 'placement_type'], base + 'domain_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'size', 'location', 'placement_type'],
                                 base + 'division_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'lowest_classification_name', 'size',
                                     'location', 'placement_type'], base + 'classification_')


def get_top_level_folders(base):
    t = []
    for (dirpath, dirnames, filenames) in walk(base):
        t.extend(dirnames)
        break
    return t


# 2015-06-12 ech - jplace files are so big that we need to process them one by one, then concatenate them.
# If we do this more than occasionally we should rewrite lineage.py to accommodate 'one tsv per jplace'.
def create_wdfw_placement_files_for_robin(base):
    for f in get_top_level_folders(base):
        print base + f
        p = create_placements(dir=base)
        l = create_lineage(ncbi_dir='/placeholder/src/data', placements=p)
        write_df_to_file(l, base + '_placements_with_lineage.tsv')


if __name__ == '__main__':
    base = '/data/wdfw/'
    # create_wdfw_placement_files_for_robin(base)
    l = read_df_from_file('/data/wdfw/wdfw_placements_with_lineage.tsv')
    # create_and_write_count_files(l, ['domain_name', 'placement_type'], base + '_domain_')
    # create_and_write_count_files(l, ['domain_name', 'division_name', 'placement_type'], base + '_division_')
    # create_and_write_count_files(l, ['domain_name', 'division_name', 'lowest_classification_name', 'placement_type'],
    #                              base + '_classification_')

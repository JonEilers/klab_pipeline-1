#!/usr/bin/env python
# Built by Eric Hervol, modified by Ryan McLaughlin

import argparse

from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
from klab.process.file_manager import create_placements, write_df_to_file
from klab.process.lineage import create_lineage


def create_lineage_files(jpath):
    jplace_dir = jpath
    lineage_file = jpath + '_placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    l = create_lineage(placements=p)
    write_df_to_file(l, lineage_file)
    return l, lineage_file


def create_and_write_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def do_the_do(jpath):
    lin, lineage_file = create_lineage_files(jpath)
    create_and_write_count_files(lin, ['gene', 'sample', 'domain_name', 'placement_type'],
                                     jpath + '_domain_')
    create_and_write_count_files(lin, ['gene', 'sample', 'domain_name', 'division_name', 
                                    'placement_type'], jpath + '_division_')
    create_and_write_count_files(lin, ['gene', 'sample', 'domain_name', 'division_name', 'class_name',
                                       'placement_type'], jpath + '_class_')
    create_and_write_count_files(lin,
                                 ['gene', 'sample', 'domain_name', 'division_name', 'class_name',
                                 'lowest_classification_name', 'placement_type'], 
                                 jpath + '_lowest_classification_')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-j_dir', help='directory containing jplace files', required=True)
    args = parser.parse_args()

    jpath = args.j_dir
    do_the_do(jpath)

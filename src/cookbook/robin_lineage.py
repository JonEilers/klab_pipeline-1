#!/usr/bin/env python

#########################
# Robin specific requests
#########################
import argparse
import os

from cookbook.mbari.transform_mbari_data import create_mbari_lineage_files
from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
from klab.process.file_manager import write_df_to_file, create_placements
from klab.process.lineage import create_lineage


def _create_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


def _create_mbari_files_for_robin(base):
    l = create_mbari_lineage_files(base)
    _create_count_files(l, ['gene', 'domain_name', 'size', 'location', 'placement_type'], base + 'domain_')
    _create_count_files(l, ['gene', 'domain_name', 'division_name', 'size', 'location', 'placement_type'],
                        base + 'division_')
    _create_count_files(l, ['gene', 'domain_name', 'division_name', 'lowest_classification_name', 'size', 'location',
                            'placement_type'], base + 'classification_')


def _create_lineage_and_count_files_for_robin(input_dir, output_dir):
    p = create_placements(dir=input_dir)
    l = create_lineage(placements=p, out_file=os.path.join(output_dir, 'placements_with_lineage.tsv'))
    _create_count_files(l, ['domain_name', 'placement_type'], os.path.join(output_dir, 'domain_'))
    _create_count_files(l, ['domain_name', 'division_name', 'placement_type'], os.path.join(output_dir, 'division_'))
    _create_count_files(l, ['domain_name', 'division_name', 'lowest_classification_name', 'placement_type'],
                        os.path.join(output_dir, 'classification_'))


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-placement_directory', help='directory with sequence placement files', required=True)
    parser.add_argument('-out_directory', help='output directory', required=True)
    args = parser.parse_args()

    _create_lineage_and_count_files_for_robin(input_dir=args.placement_directory, output_dir=args.out_directory)

#!/usr/bin/env python

import argparse

from klab.process.derived_info import add_placement_type_column, CONFIDENT
from klab.process.file_manager import read_df_from_file, CLASSIFICATION_COLUMN
from klab.analysis.diversity import create_n_way_diversity_files


def create_bb_diversity_files(placement_file, compare, out_directory):
    placements = read_df_from_file(placement_file, low_memory=False)
    # filter by confident placements
    add_placement_type_column(placements)
    p = placements[placements.placement_type == CONFIDENT]
    # filter out non-specific matches
    p = p[p['class_id'] != -1]
    p = p[p['depth'] != 'UNKNOWN']
    p = p[p['location'] != 'UNKNOWN']
    p = p[p[CLASSIFICATION_COLUMN] != 150487]  # this is just a poorly formed name that chokes R

    create_n_way_diversity_files(p, compare, out_directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-placement_file', help='placement file with lineage information', required=True)
    parser.add_argument('-compare', help='comparison column name (depth, location, year, date)', required=True)
    parser.add_argument('-out_directory', help='output directory', required=True)
    args = parser.parse_args()

    create_bb_diversity_files(args.placement_file, args.compare, args.out_directory)

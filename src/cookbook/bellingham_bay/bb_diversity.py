#!/usr/bin/env python
import argparse

from klab.process.file_manager import read_df_from_file
from klab.analysis.diversity import create_n_way_diversity_files

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-placement_file', help='placement file with lineage information', required=True)
    parser.add_argument('-compare', help='comparison column name', required=True)
    parser.add_argument('-out_directory', help='output directory', required=True)
    args = parser.parse_args()

    placements = read_df_from_file(args.placement_file)

    create_n_way_diversity_files(placements, args.compare, args.out_directory)

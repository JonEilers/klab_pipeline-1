#!/usr/bin/env python

import argparse

import pandas as pd

from klab.process.file_manager import get_files, read_df_from_file
from klab.process.lineage import create_lineage
from klab.process.derived_info import group_and_count

"""
Reads the tax_map files from a reference package to get normalization counts for placements.
"""


def get_tax_map_info(root):
    file_list = get_files(root_directory=root, extension='tax_map.csv')
    file_list.sort()

    print ('%d files to run...' % len(file_list))

    df = pd.DataFrame()
    for f in file_list:
        print ('processing %s...' % f)
        d = read_df_from_file(f)
        df = df.append(d)
    result = pd.DataFrame(df.tax_id)
    result.rename(columns={'tax_id': 'classification'}, inplace=True)
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='reference package directory', required=True)
    parser.add_argument('-ncbi_directory', help='NCBI data directory', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    d2 = get_tax_map_info(root=args.directory)
    # TODO ech 2015-11-12 - not sure about grouping or not...
    d3 = group_and_count(d2, ['classification'])
    l = create_lineage(ncbi_dir=args.ncbi_directory, placements=d3, out_file=args.out_file)

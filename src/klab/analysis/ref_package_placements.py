#!/usr/bin/env python

import argparse
import os

import pandas as pd

from klab.process.file_manager import get_files, read_df_from_file, CLASSIFICATION_COLUMN
from klab.process.lineage import create_lineage

"""
Reads the tax_map files from a reference package to get normalization counts for placements.
"""


def _get_tax_map_info(root):
    file_list = get_files(root_directory=root, extension='tax_map.csv')
    file_list.sort()
    print ('%d files to run...' % len(file_list))

    df = pd.DataFrame()
    for f in file_list:
        print ('processing %s...' % f)
        file_name = os.path.basename(f)
        cluster = file_name.split('.')[0]  # name of cluster is first part of file name
        d = read_df_from_file(f)
        d['cluster'] = pd.Series(cluster, index=d.index)  # add cluster column
        df = df.append(d)

    df.drop('seqname', axis=1, inplace=True)  # drop uneeded column
    df.rename(columns={'tax_id': CLASSIFICATION_COLUMN}, inplace=True)  # rename for consistency with lineage code
    return df


def get_ref_package_placements(root_directory, out_file=None):
    d2 = _get_tax_map_info(root_directory)
    return create_lineage(placements=d2, out_file=out_file)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='reference package directory', required=True)
    parser.add_argument('-ncbi_directory', help='NCBI data directory', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    get_ref_package_placements(root_directory=args.directory, out_file=args.out_file)

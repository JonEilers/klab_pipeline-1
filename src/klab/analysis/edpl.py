#!/usr/bin/env python

import argparse
import os
import subprocess

import pandas as pd

from klab.process.file_manager import get_files, write_df_to_file

"""
Calculates Expected Distance between Placement Locations using pplacer guppy utility.

Inspired by Ryan's EDPL_calc.py
"""


def calculate_edpl(root):
    file_list = get_files(root_directory=root, extension='.jplace')
    file_list.sort()

    print ('%d files to run...' % len(file_list))

    data = []
    for f in file_list:
        print ('processing %s...' % f)
        file_name = os.path.basename(f)
        cluster = file_name.split('.')[0]  # name of cluster is first part of file name
        edpl_out = subprocess.check_output(['guppy', 'edpl', f], stderr=subprocess.STDOUT)
        for edpl in edpl_out.split('\n'):
            if edpl:
                row = [cluster]
                row.extend(edpl.split())
                data.append(row)

    return pd.DataFrame(data=data, columns=['cluster', 'fragment_id', 'edpl'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='directory with .jplace files', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    df = calculate_edpl(root=args.directory)
    write_df_to_file(df, args.out_file)

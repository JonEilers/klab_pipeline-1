#!/usr/bin/env python

from __future__ import unicode_literals

import argparse
import os
import subprocess

import pandas as pd

from klab.process.file_manager import get_files, write_df_to_file

"""
Calculates Expected Distance between Placement Locations using pplacer guppy utility.

Inspired by Ryan's EDPL_calc.py
"""


def _calculate_edpl(root):
    file_list = get_files(root_directory=root, extension='.jplace')
    file_list.sort()

    print('%d files to run...' % len(file_list))

    data = []
    for f in file_list:
        print('processing %s...' % f)
        file_name = os.path.basename(f)
        gene = file_name.split('.')[0]  # name of gene is first part of file name
        # call "guppy edpl --pp" to calculate edpl
        edpl_out = subprocess.check_output(['guppy', 'edpl', '--pp', f], stderr=subprocess.STDOUT,
                                           universal_newlines=True)
        for edpl in edpl_out.split('\n'):
            if edpl:
                row = [gene]
                row.extend(edpl.split())
                data.append(row)

    return pd.DataFrame(data=data, columns=['gene', 'fragment_id', 'edpl'])


def get_edpl(root_directory, out_file=None):
    df = _calculate_edpl(root=root_directory)
    if out_file:
        write_df_to_file(df, out_file)
    return df


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='directory with .jplace files', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    get_edpl(root_directory=args.directory, out_file=args.out_file)

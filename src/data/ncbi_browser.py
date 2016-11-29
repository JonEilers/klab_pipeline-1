#!/usr/bin/env python

from __future__ import unicode_literals

import argparse
import os

import pandas as pd

from klab.process.file_manager import read_df_from_file

if __name__ == '__main__':  # pragma nocover
    ncbi_dir = os.path.dirname(os.path.realpath(__file__))

    parser = argparse.ArgumentParser(description='List NCBI rankings and optinoally names for a ranking.')
    parser.add_argument('-rankings', help='quote-enclosed comma-separated list of desired NCBI rankings.')
    args = parser.parse_args()

    r = []
    if args.rankings:
        r = [x.strip() for x in args.rankings.split(',')]

    nodes = read_df_from_file(os.path.join(ncbi_dir, 'nodes.tsv'))
    nodes.columns = ['taxa', 'parent', 'rank']
    print('NCBI Ranking           Count\n')
    print(nodes['rank'].value_counts(ascending=True))

    if r:
        names = read_df_from_file(os.path.join(ncbi_dir, 'names.tsv'))
        names.columns = ['taxa', 'name']
        m = pd.merge(left=nodes, right=names, on='taxa', how='left')
        d = m[m['rank'].isin(r)].sort_values(by=['rank', 'name'])
        print('\n')
        if d.empty:
            print('No rankings found matching: "%s"' % ','.join(r))
        else:
            print(d[['rank', 'name']])

#!/usr/bin/env python

import os

from klab.analysis.diversity import CLASSIFICATION_NAME_COLUMN
from klab.process.file_manager import create_placements, write_df_to_file
from klab.process.lineage import create_lineage


def _get_location_from_fragment_id(fid):
    l = fid[8:9]
    if 'B' == l:
        return 'BB6'
    elif 'N' == l:
        return 'NS10'
    elif 'E' == l:
        return 'Eliza'
    return 'UNKNOWN'


def _add_bb_location_column(df):
    df['location'] = df.fragment_id.apply(_get_location_from_fragment_id)
    return df


# TODO ech 2016-02-08 - concept of 'week 1, week 2' is pretty fuzzy, going with month_day for now
def _add_bb_date_columns(df):
    df['date'] = df.fragment_id.apply(lambda x: x[2:6])
    df['year'] = df.fragment_id.apply(lambda x: '20' + x[6:8])
    return df


def _get_depth_from_fragment_id(fid):
    d = fid[9:11]
    if 'Dp' == d:
        return 'Deep'
    elif 'CM' == d:
        return 'Chlorophyll Maximum'
    elif 'Su' == d:
        return 'Surface'
    return 'UNKNOWN'


def _add_bb_depth_column(df):
    df['depth'] = df.fragment_id.apply(_get_depth_from_fragment_id)
    return df


if __name__ == '__main__':
    data_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data')

    jplace_dir = '/Users/ehervol/Projects/WWU/bellingham_bay/test'
    placements_file = os.path.join(jplace_dir, 'placements.tsv')
    lineage_file = os.path.join(jplace_dir, 'placements_with_lineage.tsv')

    p = create_placements(dir=jplace_dir)

    _add_bb_location_column(p)
    _add_bb_date_columns(p)
    _add_bb_depth_column(p)

    write_df_to_file(p, placements_file)

    l = create_lineage(placements=p)
    l.rename(columns={'lowest_classification_name': CLASSIFICATION_NAME_COLUMN}, inplace=True)
    write_df_to_file(l, lineage_file)

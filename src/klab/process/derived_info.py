#!/usr/bin/env python

from __future__ import division

import pandas as pd

CONFIDENCE_INTERVAL = 0.05  # magic number
CONFIDENT = 'confident'
FUZZY = 'fuzzy'

# This name can create some issues because 'count' is also a pandas function. Use df['count'] instead of df.count
COUNT_COLUMN = 'count'

# remove trailing/leading spaces, lowercase, replace internal spaces with '_'
def standardize_column_headers(df):
    return df.rename(columns=lambda x: x.strip().lower().replace(' ', '_'), inplace=True)


# Might use posterior probability metric instead of like weight ratio
def add_placement_type_column(df, best_column='like_weight_ratio', next_best_column='next_best_lwr',
                              ci=CONFIDENCE_INTERVAL):
    df['placement_type'] = FUZZY
    df.loc[abs(df[best_column] - df[next_best_column]) >= ci, ['placement_type']] = CONFIDENT
    return df


# TODO ech 2015-03-03 - refactor next two methods
def group_and_count(df, columns):
    groups = df.groupby(columns)
    # this will drop any rows with null values
    counts = pd.DataFrame(groups.size())  # make a dataframe out of the count dictionary
    counts.reset_index(inplace=True)  # flatten the hierarchical indices
    counts.rename(columns={0: COUNT_COLUMN}, inplace=True)  # name the count column properly
    return counts


# calculate factor to scale counts up to largest count value
def get_normalize_factor(df, normalize_column):
    cx = group_and_count(df, [normalize_column])
    maxi = cx[COUNT_COLUMN].max(axis=1)
    cx['normalize_factor'] = maxi / cx[COUNT_COLUMN]
    cx.drop(COUNT_COLUMN, axis=1, inplace=True)
    return cx


######### specific to a data set ##########################

def _get_size_from_fragment_id(fid):
    size = fid.split('_')[0]
    if '3-20' in size:
        return 'large'
    elif '.8-3' in size:
        return 'medium'
    elif '.1-.8' in size:
        return 'small'
    return size


def add_mbari_size_column(df):
    df['size'] = df.fragment_id.apply(_get_size_from_fragment_id)
    return df


def add_mbari_location_column(df):
    df['location'] = df.fragment_id.apply(lambda x: x.split('_')[1])
    return df


def add_seastar_srr_column(df):
    df['ncbi_srr'] = df.fragment_id.apply(lambda x: x.split('.')[0])
    return df

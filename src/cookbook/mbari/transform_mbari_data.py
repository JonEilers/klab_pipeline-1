#!/usr/bin/env python

from __future__ import unicode_literals

import os

import pandas as pd

from cookbook.mbari import MBARI_2012_BASE, MBARI_2012_EDPL_FILE, MBARI_2012_LINEAGE_FILE, MBARI_2012_REF_PKG_FILE, \
    MBARI_2012_PACKAGE_DIR, MBARI_2014_BASE, MBARI_2014_EDPL_FILE, MBARI_2014_LINEAGE_FILE, MBARI_2014_REF_PKG_FILE, \
    MBARI_2014_PACKAGE_DIR, MBARI_12_14_REF_COUNTS_FILE, MBARI_12_14_MERGED_FILE, MBARI_12_16_REF_COUNTS_FILE, \
    MBARI_2016_REF_PKG_FILE, MBARI_2016_PACKAGE_DIR, MBARI_2016_EDPL_FILE, MBARI_2016_BASE, MBARI_2016_LINEAGE_FILE, \
    MBARI_12_16_MERGED_FILE
from klab.analysis.edpl import get_edpl
from klab.analysis.ref_package_placements import get_ref_package_placements
from klab.process.derived_info import add_placement_type_column, group_and_count
from klab.process.file_manager import create_placements, write_df_to_file, read_df_from_file, CLASSIFICATION_COLUMN
from klab.process.lineage import create_lineage

TOP_LEVEL = 'top level'  # start with a lower case letter to sort after domains when graphing


def _get_size_from_fragment_id(fid):
    size = fid.split('_')[0]
    if '3-20' in size:
        return 'large'
    elif '.8-3' in size:
        return 'medium'
    elif '.1-.8' in size:
        return 'small'
    return size


def _add_mbari_size_column(df):
    df['size'] = df.fragment_id.apply(_get_size_from_fragment_id)
    return df


def _add_mbari_location_column(df):
    df['location'] = df.fragment_id.apply(lambda x: x.split('_')[1])
    return df


def _add_edpl_column(df, edpl_df):
    return pd.merge(df, edpl_df, on=['fragment_id', 'gene'], how='outer')


def _merge_mbari_data(file_12, file_14, result):
    df12 = read_df_from_file(file_12)
    df14 = read_df_from_file(file_14)
    df = pd.merge(df12, df14, on='fragment_id', how='outer', suffixes=('_12', '_14'))

    # drop rows with taxa id that were removed from NCBI
    df = df[df.domain_name_12 != 'DELETED NODE']
    df = df[df.domain_name_14 != 'DELETED NODE']

    # merge and rename root and cellular organism matches
    df.ix[df.domain_name_12 == 'root', 'domain_name_12'] = TOP_LEVEL
    df.ix[df.domain_name_12 == 'cellular organisms', 'domain_name_12'] = TOP_LEVEL
    df.ix[df.domain_name_14 == 'root', 'domain_name_14'] = TOP_LEVEL
    df.ix[df.domain_name_14 == 'cellular organisms', 'domain_name_14'] = TOP_LEVEL

    df.ix[df.lowest_classification_name_12 == 'root', 'lowest_classification_name_12'] = TOP_LEVEL
    df.ix[df.lowest_classification_name_12 == 'cellular organisms', 'lowest_classification_name_12'] = TOP_LEVEL
    df.ix[df.lowest_classification_name_14 == 'root', 'lowest_classification_name_14'] = TOP_LEVEL
    df.ix[df.lowest_classification_name_14 == 'cellular organisms', 'lowest_classification_name_14'] = TOP_LEVEL

    write_df_to_file(df, result)


def _merge_mbari_domain_data(file_a, label_a, file_b, label_b, result):
    df_a = read_df_from_file(file_a, low_memory=False)
    df_a = df_a[df_a['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df_b = read_df_from_file(file_b, low_memory=False)
    df_b = df_b[df_b['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df = pd.merge(df_a, df_b, on='fragment_id', how='outer', suffixes=('_' + label_a, '_' + label_b))

    # # drop rows with taxa id that were removed from NCBI
    # df = df[df.domain_name_12 != 'DELETED NODE']
    # df = df[df.domain_name_14 != 'DELETED NODE']
    #
    # # merge and rename root and cellular organism matches
    # df.ix[df.domain_name_12 == 'root', 'domain_name_12'] = TOP_LEVEL
    # df.ix[df.domain_name_12 == 'cellular organisms', 'domain_name_12'] = TOP_LEVEL
    # df.ix[df.domain_name_14 == 'root', 'domain_name_14'] = TOP_LEVEL
    # df.ix[df.domain_name_14 == 'cellular organisms', 'domain_name_14'] = TOP_LEVEL
    #
    # df.ix[df.lowest_classification_name_12 == 'root', 'lowest_classification_name_12'] = TOP_LEVEL
    # df.ix[df.lowest_classification_name_12 == 'cellular organisms', 'lowest_classification_name_12'] = TOP_LEVEL
    # df.ix[df.lowest_classification_name_14 == 'root', 'lowest_classification_name_14'] = TOP_LEVEL
    # df.ix[df.lowest_classification_name_14 == 'cellular organisms', 'lowest_classification_name_14'] = TOP_LEVEL

    write_df_to_file(df, result)


def _merge_reference_package_data(file_a, label_a, file_b, label_b, result):
    d = read_df_from_file(file_a)
    d2 = d.drop_duplicates(CLASSIFICATION_COLUMN)
    df_a = group_and_count(d2, ['domain_name'])
    year_a = '20' + label_a

    d = read_df_from_file(file_b)
    d2 = d.drop_duplicates(CLASSIFICATION_COLUMN)
    df_b = group_and_count(d2, ['domain_name'])
    year_b = '20' + label_b

    df = pd.merge(df_a, df_b, on='domain_name', how='outer', suffixes=('_' + label_a, '_' + label_b))
    df = df[df['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df.rename(columns={'count_' + label_a: year_a, 'count_' + label_b: year_b}, inplace=True)
    df['change'] = df[year_b] / df[year_a]
    write_df_to_file(df, result)


def create_mbari_lineage_files(base, edpl=None):
    jplace_dir = base + 'analysis'
    lineage_file = base + 'placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    if edpl:
        edpl = read_df_from_file(edpl)
        p2 = _add_edpl_column(p, edpl)
    else:
        p2 = p
    l = create_lineage(placements=p2)
    add_placement_type_column(l)
    _add_mbari_size_column(l)
    _add_mbari_location_column(l)
    write_df_to_file(l, lineage_file)
    return l


########################################################################
# do all the mbari data massage, skipping steps if results already exist
########################################################################
if __name__ == '__main__':
    # reference package placement counts
    if not os.path.isfile(MBARI_2012_REF_PKG_FILE):
        get_ref_package_placements(root_directory=MBARI_2012_PACKAGE_DIR, out_file=MBARI_2012_REF_PKG_FILE)
    if not os.path.isfile(MBARI_2014_REF_PKG_FILE):
        get_ref_package_placements(root_directory=MBARI_2014_PACKAGE_DIR, out_file=MBARI_2014_REF_PKG_FILE)
    if not os.path.isfile(MBARI_2016_REF_PKG_FILE):
        get_ref_package_placements(root_directory=MBARI_2016_PACKAGE_DIR, out_file=MBARI_2016_REF_PKG_FILE)

    # binned and merged ref package counts
    if not os.path.isfile(MBARI_12_14_REF_COUNTS_FILE):
        _merge_reference_package_data(MBARI_2012_REF_PKG_FILE, '12', MBARI_2014_REF_PKG_FILE, '14',
                                      MBARI_12_14_REF_COUNTS_FILE)
    if not os.path.isfile(MBARI_12_16_REF_COUNTS_FILE):
        _merge_reference_package_data(MBARI_2012_REF_PKG_FILE, '12', MBARI_2016_REF_PKG_FILE, '16',
                                      MBARI_12_16_REF_COUNTS_FILE)

    # edpl calculations
    if not os.path.isfile(MBARI_2012_EDPL_FILE):
        get_edpl(root_directory=MBARI_2012_BASE + 'analysis', out_file=MBARI_2012_EDPL_FILE)
    if not os.path.isfile(MBARI_2014_EDPL_FILE):
        get_edpl(root_directory=MBARI_2014_BASE + 'analysis', out_file=MBARI_2014_EDPL_FILE)
    if not os.path.isfile(MBARI_2016_EDPL_FILE):
        get_edpl(root_directory=MBARI_2016_BASE + 'analysis', out_file=MBARI_2016_EDPL_FILE)

    # lineage and derived data
    if not os.path.isfile(MBARI_2012_LINEAGE_FILE):
        create_mbari_lineage_files(base=MBARI_2012_BASE, edpl=MBARI_2012_EDPL_FILE)
    if not os.path.isfile(MBARI_2014_LINEAGE_FILE):
        create_mbari_lineage_files(base=MBARI_2014_BASE, edpl=MBARI_2014_EDPL_FILE)
    if not os.path.isfile(MBARI_2016_LINEAGE_FILE):
        create_mbari_lineage_files(base=MBARI_2016_BASE, edpl=MBARI_2016_EDPL_FILE)

    # # # merge lineage files
    # # if not os.path.isfile(MBARI_12_14_MERGED_FILE):
    # #     _merge_mbari_data(file_12=MBARI_2012_LINEAGE_FILE, file_14=MBARI_2014_LINEAGE_FILE,
    # #                       result=MBARI_12_14_MERGED_FILE)

    # merge domain lineage files
    if not os.path.isfile(MBARI_12_14_MERGED_FILE):
        _merge_mbari_domain_data(file_a=MBARI_2012_LINEAGE_FILE, label_a='12', file_b=MBARI_2014_LINEAGE_FILE,
                                 label_b='14', result=MBARI_12_14_MERGED_FILE)
    if not os.path.isfile(MBARI_12_16_MERGED_FILE):
        _merge_mbari_domain_data(file_a=MBARI_2012_LINEAGE_FILE, label_a='12', file_b=MBARI_2016_LINEAGE_FILE,
                                 label_b='16', result=MBARI_12_16_MERGED_FILE)

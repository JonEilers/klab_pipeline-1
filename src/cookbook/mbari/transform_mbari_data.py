#!/usr/bin/env python
import os

import pandas as pd

from klab.analysis.edpl import get_edpl
from klab.analysis.ref_package_placements import get_ref_package_placements
from klab.process.derived_info import add_placement_type_column, group_and_count
from klab.process.file_manager import create_placements, write_df_to_file, read_df_from_file
from klab.process.lineage import create_lineage
from cookbook.mbari import NCBI_DATA_DIR, MBARI_2012_BASE, MBARI_2014_BASE, MBARI_2012_EDPL_FILE, \
    MBARI_2014_EDPL_FILE, MBARI_2012_LINEAGE_FILE, MBARI_2014_LINEAGE_FILE, MBARI_12_14_MERGED_FILE, \
    MBARI_2012_REF_PKG_FILE, MBARI_2012_PACKAGE_DIR, MBARI_2014_PACKAGE_DIR, MBARI_2014_REF_PKG_FILE, MBARI_DATA_DIR

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
    return pd.merge(df, edpl_df, on=['fragment_id', 'cluster'], how='outer')


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


def _merge_reference_package_data(file_12, file_14, result):
    d = read_df_from_file(file_12)
    d2 = d.drop_duplicates('classification')
    d12 = group_and_count(d2, ['domain_name'])

    d = read_df_from_file(file_14)
    d2 = d.drop_duplicates('classification')
    d14 = group_and_count(d2, ['domain_name'])

    df = pd.merge(d12, d14, on='domain_name', how='outer', suffixes=('_12', '_14'))
    df = df[df['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota', 'Viruses'])]
    df.rename(columns={'count_12': '2012', 'count_14': '2014'}, inplace=True)
    df['change'] = df['2014'] / df['2012']
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
    l = create_lineage(ncbi_dir=NCBI_DATA_DIR, placements=p2)
    add_placement_type_column(l)
    _add_mbari_size_column(l)
    _add_mbari_location_column(l)
    write_df_to_file(l, lineage_file)
    return l


########################################################################
# do all the mbari data massage, skipping steps if results already exist
########################################################################
if __name__ == '__main__':
    # edpl calculations
    if not os.path.isfile(MBARI_2012_EDPL_FILE):
        get_edpl(root_directory=MBARI_2012_BASE + 'analysis', out_file=MBARI_2012_EDPL_FILE)
    if not os.path.isfile(MBARI_2014_EDPL_FILE):
        get_edpl(root_directory=MBARI_2014_BASE + 'analysis', out_file=MBARI_2014_EDPL_FILE)

    # reference package placement counts
    if not os.path.isfile(MBARI_2012_REF_PKG_FILE):
        get_ref_package_placements(root_directory=MBARI_2012_PACKAGE_DIR, ncbi_directory=NCBI_DATA_DIR,
                                   out_file=MBARI_2012_REF_PKG_FILE)
    if not os.path.isfile(MBARI_2014_REF_PKG_FILE):
        get_ref_package_placements(root_directory=MBARI_2014_PACKAGE_DIR, ncbi_directory=NCBI_DATA_DIR,
                                   out_file=MBARI_2014_REF_PKG_FILE)

    # binned and merged ref package counts
    if not os.path.isfile(MBARI_DATA_DIR + 'mbari_ref_counts.tsv'):
        _merge_reference_package_data(MBARI_2012_REF_PKG_FILE, MBARI_2014_REF_PKG_FILE,
                                      MBARI_DATA_DIR + 'mbari_ref_counts.tsv')

    # lineage and derived data
    if not os.path.isfile(MBARI_2012_LINEAGE_FILE):
        create_mbari_lineage_files(base=MBARI_2012_BASE, edpl=MBARI_2012_EDPL_FILE)
    if not os.path.isfile(MBARI_2014_LINEAGE_FILE):
        create_mbari_lineage_files(base=MBARI_2014_BASE, edpl=MBARI_2014_EDPL_FILE)

    # merge lineage files
    if not os.path.isfile(MBARI_12_14_MERGED_FILE):
        _merge_mbari_data(file_12=MBARI_2012_LINEAGE_FILE, file_14=MBARI_2014_LINEAGE_FILE,
                          result=MBARI_12_14_MERGED_FILE)

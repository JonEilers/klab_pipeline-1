#!/usr/bin/env python

import pandas as pd

from cookbook.mbari import MBARI_DATA_DIR
from klab.process.file_manager import write_df_to_file, read_df_from_file

TOP_LEVEL = 'Top Level'


def _merge_mbari_data():
    df12 = read_df_from_file(MBARI_DATA_DIR + '2012_MBARI_cog_placements_with_lineage.tsv')
    df14 = read_df_from_file(MBARI_DATA_DIR + '2014_MBARI_cog_placements_with_lineage.tsv')
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

    write_df_to_file(df, MBARI_DATA_DIR + 'MBARI_merged.tsv')


if __name__ == '__main__':
    _merge_mbari_data()

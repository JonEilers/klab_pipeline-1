#!/usr/bin/env python

from klab.process.file_manager import create_placements, write_df_to_file
from klab.process.lineage import create_lineage


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


def create_mbari_lineage_files(base):
    jplace_dir = base + 'analysis'
    lineage_file = base + 'placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    l = create_lineage(ncbi_dir='/placeholder/src/data', placements=p)
    _add_mbari_size_column(l)
    _add_mbari_location_column(l)
    write_df_to_file(l, lineage_file)
    return l


if __name__ == '__main__':
    create_mbari_lineage_files('/data/2014_MBARI_cog_')
    create_mbari_lineage_files('/data/2012_MBARI_cog_')

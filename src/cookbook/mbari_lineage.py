#!/usr/bin/env python

from klab.process.derived_info import group_and_count, FUZZY, CONFIDENT
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


def create_lineage_files(base):
    jplace_dir = base + 'analysis'
    lineage_file = base + 'placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    l = create_lineage(ncbi_dir='/placeholder/src/data', placements=p)
    _add_mbari_size_column(l)
    _add_mbari_location_column(l)
    write_df_to_file(l, lineage_file)
    return l


def create_and_write_count_files(lineage, grouping, path):
    c = group_and_count(lineage, grouping)
    fuzzy_counts = c[c.placement_type == FUZZY]
    confident_counts = c[c.placement_type == CONFIDENT]
    write_df_to_file(fuzzy_counts, path + 'count_fuzzy.tsv')
    write_df_to_file(confident_counts, path + 'count_confident.tsv')


# ech 2015-03-07 - take the repetition out of rebuilding the mbari data for Robin
def do_the_do(base):
    l = create_lineage_files(base)

    create_and_write_count_files(l, ['cluster', 'domain_name', 'size', 'location', 'placement_type'], base + 'domain_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'size', 'location', 'placement_type'],
                                 base + 'division_')
    create_and_write_count_files(l, ['cluster', 'domain_name', 'division_name', 'lowest_classification_name', 'size',
                                     'location', 'placement_type'], base + 'classification_')


if __name__ == '__main__':
    create_lineage_files('/data/2014_MBARI_cog_')
    create_lineage_files('/data/2012_MBARI_cog_')

#!/usr/bin/env python

from klab.process.file_manager import create_placements
from klab.process.lineage import create_lineage


def add_seastar_srr_column(df):
    df['ncbi_srr'] = df.fragment_id.apply(lambda x: x.split('.')[0])
    return df


def create_lineage_files(base):
    jplace_dir = base + 'analysis'
    lineage_file = base + 'placements_with_lineage.tsv'

    p = create_placements(dir=jplace_dir)
    create_lineage(ncbi_dir='/placeholder/src/data', placements=p, out_file=lineage_file)

# ech 2015-03-06 - take the repetition out of rebuilding the seastar data
if __name__ == '__main__':
    # create_lineage_files('/shared_projects/seastar/data/bm_ssu_')
    # create_lineage_files('/shared_projects/seastar/data/bm_viral_')
    create_lineage_files('/shared_projects/seastar/data/bm_cog_')

    # create_lineage_files('/shared_projects/seastar/data/virome_ssu_')
    # create_lineage_files('/shared_projects/seastar/data/virome_viral_')

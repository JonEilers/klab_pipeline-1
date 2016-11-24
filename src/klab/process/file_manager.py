#!/usr/bin/env python

from __future__ import unicode_literals

import argparse
import os

import pandas as pd
from future.utils import bytes_to_native_str

try:
    import simplejson as json
except ImportError:  # pragma nocover
    import json  # simplejson has better feedback on parsing failures

CLASSIFICATION_COLUMN = 'classification'
PLACEMENT_COLUMN = 'post_prob'
NEXT_BEST_PLACEMENT_COLUMN = 'next_best_pp'
TAB_CHAR = bytes_to_native_str(b'\t')  # 2.7/3.5 compatible


def get_files(root_directory, extension='.jplace'):
    filtered_files = []
    extension_length = len(extension)
    for root, subdirList, files in os.walk(os.path.abspath(root_directory)):
        for name in files:
            if name[-extension_length:] == extension:
                filtered_files.append(os.path.join(root, name))
    return filtered_files


def get_json_contents(file_name):
    f = open(file_name)
    json_data = None
    try:
        json_data = json.load(f)
    except Exception as e:  # pragma nocover
        print('json error with file %s - skipping\n%s' % (f.name, e.message))
    finally:
        f.close()
    return json_data


def read_df_from_file(file_name, low_memory=True):
    if not os.path.exists(file_name):
        raise IOError('File %s not found.' % file_name)

    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.tsv':
        return pd.read_table(file_name, low_memory=low_memory)
    elif ext == '.csv':
        return pd.read_csv(file_name, low_memory=low_memory)
    # need PyTables et al for hdf5 storage and we haven't needed the access efficiency (yet)
    # elif ext in ('.h5', '.hdf5'):
    #     return pd.read_hdf(file_name, 'table')
    else:
        raise ValueError('unknown file format')


def write_df_to_file(df, file_name, write_index=False):
    ext = os.path.splitext(file_name)[1].lower()
    if ext == '.tsv':
        df.to_csv(file_name, index=write_index, sep=TAB_CHAR)
    elif ext == '.csv':
        df.to_csv(file_name, index=write_index)
    # elif ext in ('.h5', '.hdf5'):
    #     # need PyTables et al for hdf5 storage
    #     df.to_hdf(file_name, 'table')
    else:
        raise ValueError('unknown file format')


def _build_data_frame_from_jplace_files(root):
    column_names = ['fragment_id', 'gene', 'sample']
    files = get_files(root)
    if not files:
        raise IOError('No jplace files were found.')

    # TODO ech 2015-01-24 - create gene/tree table (maybe)
    data = []
    for path in files:
        contents = get_json_contents(path)
        if contents and contents['placements'] != []:  # Ryan add and ... to deal with empty jplace files 03/04/2016
            file_name = os.path.basename(path)
            gene = file_name.split('.')[0]  # name of gene is first part of file name
            # TODO ech 2015-01-26 - too 'clever', and assumes all fields are same in all files
            if len(column_names) == 3:
                column_names.extend(contents['fields'])
            items = contents['placements']
            for item in items:
                fragments = []
                for fragment in item['nm']:
                    fragment_id = fragment[0]
                    # assumes that underscores are used and first thing is sample name
                    sample = fragment_id.split('_')[0]
                    fragments.append([fragment_id, gene, sample])

                matches = []
                for p in item['p'][:2]:  # just take the first two elements
                    matches.append(p)

                # create a row for each cross product of 'nm' and top 2 'p' items
                for fragment in fragments:
                    for match in matches:
                        row = []
                        row.extend(fragment)
                        row.extend(match)
                        data.append(row)

    return pd.DataFrame(data=data, columns=column_names)


def _prune_unwanted_rows(df):
    # shift some columns up to do easier comparison
    df[NEXT_BEST_PLACEMENT_COLUMN] = df[PLACEMENT_COLUMN].shift(-1)  # 'next posterior probability'
    df['nfid'] = df['fragment_id'].shift(-1)  # 'next fragment_id'

    single_placements = df[PLACEMENT_COLUMN] == 1
    best_placements = df.fragment_id == df.nfid
    df.loc[single_placements, [
        NEXT_BEST_PLACEMENT_COLUMN]] = 0  # clear next best posterior probability for single placements

    good_stuff = df[single_placements | best_placements]
    r = good_stuff.ix[:, :-1]  # drop next_fragment_id column
    r.reset_index(inplace=True, drop=True)
    return r


# TODO ech 2015-02-13 - not sure how these are creeping into the 2012 data - build test with relevant files
# TODO ech 2015-10-28 - don't actually see these in the 2012 data anymore
# TODO ech 2015-02-14 - will need to deal with dups across clusters (KOGs & TIGRs, etc)
def _fix_dup_problem_with_hack(df):
    # data_frame.sort(columns=['fragment_id', 'gene', CLASSIFICATION_COLUMN, PLACEMENT_COLUMN],
    # ascending=[True, True, True, False], inplace=True)
    # TODO ech 2015-02-13 - can probably use 'drop_duplicates' here
    grouped = df.groupby(['fragment_id'])
    index = [gp_keys[0] for gp_keys in grouped.groups.values()]
    return df.reindex(index)


def create_placements(dir, out_file=None):
    raw_data = _build_data_frame_from_jplace_files(dir)
    pruned_data = _prune_unwanted_rows(raw_data)
    # deduped_data = _fix_dup_problem_with_hack(pruned_data)
    # coerce CLASSIFICATION_COLUMN to int - will be needed later when matching
    pruned_data[CLASSIFICATION_COLUMN] = pruned_data[CLASSIFICATION_COLUMN].astype(int)
    if out_file:  # pragma nocover
        write_df_to_file(pruned_data, out_file)
    return pruned_data


if __name__ == '__main__':  # pragma nocover
    parser = argparse.ArgumentParser(description='Create a placement file from a directory of jplace files.')
    parser.add_argument('-directory', help='directory with .jplace files', required=True)
    parser.add_argument('-out_file', help='output file (tsv or csv format)', required=True)
    args = parser.parse_args()

    create_placements(dir=args.directory, out_file=args.out_file)

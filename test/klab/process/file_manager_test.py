#!/usr/bin/env python

from __future__ import unicode_literals

import os

import pytest

import klab.process.file_manager as file_manager

DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../../data'))


def test_read_df_from_file():
    with pytest.raises(IOError) as ioe:
        file_manager.read_df_from_file('non-existent-file.tsv')
    assert 'non-existent-file.tsv not found' in str(ioe.value)

    with pytest.raises(ValueError) as ve:
        file_manager.read_df_from_file(os.path.join(DATA_DIR, 'sequence.fasta'))
    assert 'unknown file format' in str(ve.value)

    df = file_manager.read_df_from_file(os.path.join(DATA_DIR, 'test_data.tsv'))
    assert 7 == len(df.index)
    assert 9 == len(df.columns)

    df = file_manager.read_df_from_file(os.path.join(DATA_DIR, 'test_data.csv'))
    assert 7 == len(df.index)
    assert 9 == len(df.columns)


def test_write_df_from_file():
    with pytest.raises(ValueError) as ve:
        file_manager.write_df_to_file(None, 'sequence.fasta')
    assert 'unknown file format' in str(ve.value)


def test_build_data_frame_from_jplace_files():
    with pytest.raises(IOError) as ioe:
        file_manager._build_data_frame_from_jplace_files('non-existent-dir')
    assert 'No jplace files were found' in str(ioe.value)

    df = file_manager._build_data_frame_from_jplace_files(DATA_DIR)
    delta = 0.000001

    assert 134 == len(df.index)
    assert 11 == len(df.columns)

    assert '.1-.8_coastal_FHGDIPM01D4PA5_4' == df.fragment_id[0]
    assert 'COG0001' == df.gene[0]
    assert '2' == df.classification[0]
    assert abs(0.087771 - df.distal_length[0]) <= delta
    assert 1043 == df.edge_num[0]
    assert abs(0.304988 - df.like_weight_ratio[0]) <= delta
    assert abs(-24551.096813 - df.likelihood[0]) <= delta
    assert abs(0.051685 - df.marginal_like[0]) <= delta
    assert abs(1.961135 - df.pendant_length[0]) <= delta
    assert abs(0.002871 - df.post_prob[0]) <= delta
    assert '.1-.8' == df['sample'][0]  # sample is also a function, so have to use [''] notation


def test_classification_data_type_issue():
    df = file_manager._build_data_frame_from_jplace_files(DATA_DIR)
    assert 'object' == str(df[file_manager.CLASSIFICATION_COLUMN].dtypes)

    df2 = file_manager.create_placements(DATA_DIR)
    assert 'int64' == str(df2[file_manager.CLASSIFICATION_COLUMN].dtypes)


# TODO ech 2015-03-09 - implement this
def test_prune_unwanted_rows():
    pass


# TODO ech 2015-03-09 - implement this
def test_fix_dup_problem_with_hack():
    pass

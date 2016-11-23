#!/usr/bin/env python

from __future__ import unicode_literals

import pandas as pd

import klab.process.lineage as lineage
from klab.process.file_manager import CLASSIFICATION_COLUMN

node_dict = {
    1: (1, lineage.NO_RANK),  # root
    131567: (1, lineage.NO_RANK),  # cellular organisms
    2: (131567, 'superkingdom'),  # bacteria
    6: (2, 'genus'),  # rest of these are bogus nodes
    7: (6, 'species'),
    9: (7, lineage.NO_RANK),
    17: (16, lineage.NO_RANK),
    18: (2, lineage.NO_RANK),
    19: (18, lineage.NO_RANK),
    56: (9, 'variety'),
}

name_dict = {
    lineage.MISSING_ID: lineage.NO_MATCH,
    1: 'root',
    131567: 'cellular organisms',
    2: 'bacteria',
    6: 'bact division',
    7: 'bact class'
}

merged_dict = {
    13: 7,  # triskaidekaphobics unite!
    30: 50,  # 50 is the new 30 :-)
}

del_list = [43]


def test_get_specific_taxonomy_levels2():
    t = ['domain', 'class']
    l = [2, 6, 7, 45]
    r = ['domain', 'division', 'class', 'species']
    assert lineage.MISSING_ID_LIST[:3] == lineage._get_specific_taxonomy_levels(t, [], r)
    assert [2, 7, 45] == lineage._get_specific_taxonomy_levels(t, l, r)
    assert [6, 45, 45] == lineage._get_specific_taxonomy_levels(['division', 'species'], l, r)
    assert [lineage.MISSING_ID, 7, lineage.MISSING_ID, 45] == \
           lineage._get_specific_taxonomy_levels(['superkingdom', 'class', 'phylum'], l, r)


def test_full_taxonomy_levels():
    t = ['domain', 'division', 'class', 'other1', 'other2', 'lowest']
    assert ['domain', 'division', 'class', 'lowest'] == lineage._get_top_three_and_lowest_levels(t)


def test_domain_div_class():
    t = ['domain', 'division', 'class']
    assert ['domain', 'division', 'class', 'class'] == lineage._get_top_three_and_lowest_levels(t)


def test_domain_div():
    t = ['domain', 'division']
    assert ['domain', 'division', lineage.MISSING_ID, 'division'] == lineage._get_top_three_and_lowest_levels(t)


def test_domain():
    t = ['domain']
    assert ['domain', lineage.MISSING_ID, lineage.MISSING_ID, 'domain'] == lineage._get_top_three_and_lowest_levels(t)


def test_no_taxa():
    t = []
    assert lineage.MISSING_ID_LIST[:4] == lineage._get_top_three_and_lowest_levels(t)


def test_no_nuthin():
    assert lineage.MISSING_ID_LIST[:4] == lineage._get_top_three_and_lowest_levels(None)


def test_get_lineage():
    assert ([666], [lineage.NO_RANK]) == lineage.get_lineage(node_dict, 666)  # not in dictionary
    assert ([1], [lineage.NO_RANK]) == lineage.get_lineage(node_dict, 1)  # root
    assert ([131567], [lineage.NO_RANK]) == lineage.get_lineage(node_dict, 131567)  # cellular organisms
    assert ([2], ['superkingdom']) == lineage.get_lineage(node_dict, 2)  # if not 131567 or 1, strip them off
    assert ([2, 6, 7, 9, 56], ['superkingdom', 'genus', 'species', 'no rank', 'variety']) == \
           lineage.get_lineage(node_dict, 56)


def test_build_lineage_matrix_full():
    placements = pd.DataFrame([2, 6, 2, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
    assert [[2], [2, 6], [2, 6, 7, 9, 56]] == lineage.build_lineage_matrix(node_dict, placements, full_taxa=True)


def test_build_lineage_matrix_first_three():
    placements = pd.DataFrame([2, 6, 2, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
    assert [[1, 2, -1, -1, 2], [2, 2, 6, -1, 6], [5, 2, 6, 7, 56]] == \
           lineage.build_lineage_matrix(node_dict, placements)


def test_build_lineage_matrix_specific_taxa():
    placements = pd.DataFrame([2, 6, 2, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
    assert [[1, 2, -1, 2], [2, 2, -1, 6], [5, 2, 7, 56]] == \
           lineage.build_lineage_matrix(node_dict, placements, taxa_list=['superkingdom', 'species'])


def test_build_lineage_frame():
    placements = pd.DataFrame([2, 6, 2, 6, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
    lf = lineage._build_lineage_frame(node_dict, placements)
    assert 3 == len(lf.index)
    assert ['taxa_depth', 'domain_id', 'division_id', 'class_id', CLASSIFICATION_COLUMN] == \
           list(lf.columns.values)
    # first row
    assert 1 == lf.taxa_depth[0]
    assert 2 == lf.domain_id[0]
    assert -1 == lf.division_id[0]
    assert -1 == lf.class_id[0]
    assert 2 == lf.classification[0]
    # second row
    assert 2 == lf.taxa_depth[1]
    assert 2 == lf.domain_id[1]
    assert 6 == lf.division_id[1]
    assert -1 == lf.class_id[1]
    assert 6 == lf.classification[1]
    # third row
    assert 5 == lf.taxa_depth[2]
    assert 2 == lf.domain_id[2]
    assert 6 == lf.division_id[2]
    assert 7 == lf.class_id[2]
    assert 56 == lf.classification[2]


def test_get_name_from_taxa_id():
    assert 'bacteria' == lineage.get_name_from_taxa_id(2, name_dict, del_list)
    assert lineage.NO_NAME == lineage.get_name_from_taxa_id(89, name_dict, del_list)
    assert lineage.DELETED_NAME == lineage.get_name_from_taxa_id(43, name_dict, del_list)
    assert lineage.NO_MATCH == lineage.get_name_from_taxa_id(lineage.MISSING_ID, name_dict, del_list)


def test_update_classification_ids():
    df = pd.DataFrame(data=[5, 13, 30], columns=[CLASSIFICATION_COLUMN])
    lineage._update_classification_ids(df, merged_dict)
    assert 5 == df[CLASSIFICATION_COLUMN][0]
    assert 7 == df[CLASSIFICATION_COLUMN][1]
    assert 50 == df[CLASSIFICATION_COLUMN][2]


def test_create_linneage():
    placements = pd.DataFrame([2, 6, 2, 56], columns=[CLASSIFICATION_COLUMN])
    df = lineage.create_lineage(placements=placements, node_dict=node_dict, name_dict=name_dict,
                                merged_dict=merged_dict, deleted_list=del_list)
    assert 4 == len(df.index)
    assert ['classification', 'taxa_depth', 'domain_id', 'division_id', 'class_id', 'domain_name', 'division_name',
            'class_name', 'lowest_classification_name'] == list(df.columns)

    df = lineage.create_lineage(placements=placements, taxa_list=['superkingdom', 'class'], node_dict=node_dict,
                                name_dict=name_dict, merged_dict=merged_dict, deleted_list=del_list)
    assert 4 == len(df.index)
    assert ['classification', 'taxa_depth', 'superkingdom_id', 'class_id', 'superkingdom_name', 'class_name',
            'lowest_classification_name'] == list(df.columns)

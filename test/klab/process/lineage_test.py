import unittest

import pandas as pd

import klab.process.lineage as lineage
from klab.process.file_manager import CLASSIFICATION_COLUMN

nodes_dict = {
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


class TestLineage(unittest.TestCase):
    def test_full_taxonomy_levels(self):
        t = ['domain', 'division', 'class', 'other1', 'other2', 'lowest']
        self.assertEqual(['domain', 'division', 'class', 'lowest'], lineage._get_specific_taxonomy_levels(t))

    def test_domain_div_class(self):
        t = ['domain', 'division', 'class']
        self.assertEqual(['domain', 'division', 'class', 'class'], lineage._get_specific_taxonomy_levels(t))

    def test_domain_div(self):
        t = ['domain', 'division']
        self.assertEqual(['domain', 'division', lineage.MISSING_ID, 'division'],
                         lineage._get_specific_taxonomy_levels(t))

    def test_domain(self):
        t = ['domain']
        self.assertEqual(['domain', lineage.MISSING_ID, lineage.MISSING_ID, 'domain'],
                         lineage._get_specific_taxonomy_levels(t))

    def test_no_taxa(self):
        t = []
        self.assertEqual(lineage.MISSING_ID_LIST, lineage._get_specific_taxonomy_levels(t))

    def test_no_nuthin(self):
        self.assertEqual(lineage.MISSING_ID_LIST, lineage._get_specific_taxonomy_levels(None))

    def test_get_lineage(self):
        self.assertEqual(([666], [lineage.NO_RANK]), lineage.get_lineage(nodes_dict, 666))  # not in dictionary
        self.assertEqual(([1], [lineage.NO_RANK]), lineage.get_lineage(nodes_dict, 1))  # root
        self.assertEqual(([131567], [lineage.NO_RANK]), lineage.get_lineage(nodes_dict, 131567))  # cellular organisms
        self.assertEqual(([2], ['superkingdom']),
                         lineage.get_lineage(nodes_dict, 2))  # if not 131567 or 1, strip them off
        self.assertEqual(([2, 6, 7, 9, 56], ['superkingdom', 'genus', 'species', 'no rank', 'variety']),
                         lineage.get_lineage(nodes_dict, 56))

    def test_build_lineage_matrix_full(self):
        placements = pd.DataFrame([2, 6, 2, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
        self.assertEqual([[2], [2, 6], [2, 6, 7, 9, 56]], lineage.build_lineage_matrix(nodes_dict, placements, True))

    def test_build_lineage_matrix_partial(self):
        placements = pd.DataFrame([2, 6, 2, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
        self.assertEqual([[1, 2, -1, -1, 2], [2, 2, 6, -1, 6], [5, 2, 6, 7, 56]],
                         lineage.build_lineage_matrix(nodes_dict, placements, False))

    def test_build_lineage_frame(self):
        placements = pd.DataFrame([2, 6, 2, 6, 6, 6, 56], columns=[CLASSIFICATION_COLUMN])
        lf = lineage._build_lineage_frame(nodes_dict, placements)
        self.assertEqual(3, len(lf.index))
        self.assertEqual(['taxa_depth', 'domain_id', 'division_id', 'class_id', CLASSIFICATION_COLUMN],
                         list(lf.columns.values))
        # first row
        self.assertEqual(1, lf.taxa_depth[0])
        self.assertEqual(2, lf.domain_id[0])
        self.assertEqual(-1, lf.division_id[0])
        self.assertEqual(-1, lf.class_id[0])
        self.assertEqual(2, lf.classification[0])
        # second row
        self.assertEqual(2, lf.taxa_depth[1])
        self.assertEqual(2, lf.domain_id[1])
        self.assertEqual(6, lf.division_id[1])
        self.assertEqual(-1, lf.class_id[1])
        self.assertEqual(6, lf.classification[1])
        # third row
        self.assertEqual(5, lf.taxa_depth[2])
        self.assertEqual(2, lf.domain_id[2])
        self.assertEqual(6, lf.division_id[2])
        self.assertEqual(7, lf.class_id[2])
        self.assertEqual(56, lf.classification[2])

    def test_get_name_from_taxa_id(self):
        self.assertEqual('bacteria', lineage.get_name_from_taxa_id(2, name_dict, del_list))
        self.assertEqual(lineage.NO_NAME, lineage.get_name_from_taxa_id(89, name_dict, del_list))
        self.assertEqual(lineage.DELETED_NAME, lineage.get_name_from_taxa_id(43, name_dict, del_list))
        self.assertEqual(lineage.NO_MATCH, lineage.get_name_from_taxa_id(lineage.MISSING_ID, name_dict, del_list))

    def test_update_classification_ids(self):
        df = pd.DataFrame(data=[5, 13, 30], columns=[CLASSIFICATION_COLUMN])
        lineage._update_classification_ids(df, merged_dict)
        self.assertEqual(5, df[CLASSIFICATION_COLUMN][0])
        self.assertEqual(7, df[CLASSIFICATION_COLUMN][1])
        self.assertEqual(50, df[CLASSIFICATION_COLUMN][2])

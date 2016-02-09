import unittest
import pandas as pd

from klab.analysis.diversity import _build_lineage_dict, _calculate_similarity, _build_similarity_matrix, \
    build_similarity_frame, CLASSIFICATION_NAME_COLUMN
from klab.process.file_manager import CLASSIFICATION_COLUMN


node_dict = {
    1: 1,  # root
    131567: 1,  # cellular organisms
    2: 131567,  # bacteria
    2759: 131567,  # eukaryota
    6: 2,  # rest of these are bogus nodes
    7: 6,
    9: 7,
    16: 131567,
    17: 16,
    18: 2,
    19: 18,
    56: 9,
}


class TestDiversity(unittest.TestCase):
    def test_calculate_similarity(self):
        placements = pd.DataFrame(node_dict.keys(), columns=[CLASSIFICATION_COLUMN])
        ld = _build_lineage_dict(node_dict, placements)

        self.assertAlmostEqual(0.0, _calculate_similarity(ld, -1, -2), 5)  # both not in lineage
        self.assertAlmostEqual(0.0, _calculate_similarity(ld, -1, 2), 5)  # one not in list
        self.assertAlmostEqual(0.0, _calculate_similarity(ld, 1, 2), 5)  # root gets pruned out
        self.assertAlmostEqual(0.0, _calculate_similarity(ld, 2, 2759), 5)  # no similarity between domains
        self.assertAlmostEqual(0.0, _calculate_similarity(ld, 56, 2759), 5)  # ditto
        self.assertAlmostEqual(1.0, _calculate_similarity(ld, 56, 56), 5)  # same item is always 1
        self.assertAlmostEqual(1.0, _calculate_similarity(ld, -1, -1), 5)  # still 1, even if not in lineage
        self.assertAlmostEqual(0.5, _calculate_similarity(ld, 2, 6), 5)
        self.assertAlmostEqual(0.5, _calculate_similarity(ld, 6, 2), 5)
        self.assertAlmostEqual(0.3333, _calculate_similarity(ld, 2, 7), 4)
        self.assertAlmostEqual(0.25, _calculate_similarity(ld, 2, 9), 5)
        self.assertAlmostEqual(0.5, _calculate_similarity(ld, 18, 6), 5)
        self.assertAlmostEqual(0.5, _calculate_similarity(ld, 6, 9), 5)
        self.assertAlmostEqual(0.75, _calculate_similarity(ld, 7, 9), 5)
        self.assertAlmostEqual(0.8, _calculate_similarity(ld, 56, 9), 5)

    def test_build_similarity_matrix(self):
        dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
        abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
        sm, k = _build_similarity_matrix(node_dict, abundance)
        self.assertEqual(4, len(k))
        # first row
        self.assertEqual(1, sm[0][0])
        self.assertEqual(0.5, sm[0][1])
        self.assertEqual(0.25, sm[0][2])
        self.assertEqual(0, sm[0][3])
        # second row
        self.assertEqual(0.5, sm[1][0])
        self.assertEqual(1, sm[1][1])
        self.assertEqual(0.5, sm[1][2])
        self.assertEqual(0, sm[1][3])
        # third row
        self.assertEqual(0.25, sm[2][0])
        self.assertEqual(0.5, sm[2][1])
        self.assertEqual(1, sm[2][2])
        self.assertEqual(0, sm[2][3])
        # fourth row
        self.assertEqual(0, sm[3][0])
        self.assertEqual(0, sm[3][1])
        self.assertEqual(0, sm[3][2])
        self.assertEqual(1, sm[3][3])

    def test_build_lineage_dict(self):
        dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
        abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
        ld = _build_lineage_dict(node_dict, abundance)
        self.assertEqual([2, 6, 9, 17], sorted(ld.keys()))
        self.assertEqual([2], ld.get(2))
        self.assertEqual([2, 6], ld.get(6))
        self.assertEqual([2, 6, 7, 9], ld.get(9))
        self.assertEqual([16, 17], ld.get(17))

    def test_build_similarity_frame(self):
        dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
        abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
        sim = build_similarity_frame(abundance, node_dict)

        self.assertEquals(4, len(sim.index))
        self.assertEquals(['two', 'six', 'nine', 'seventeen'], list(sim.columns))
        # first row
        self.assertEqual(1, sim.two[0])
        self.assertEqual(0.5, sim.six[0])
        self.assertEqual(0.25, sim.nine[0])
        self.assertEqual(0, sim.seventeen[0])
        # second row
        self.assertEqual(0.5, sim.two[1])
        self.assertEqual(1, sim.six[1])
        self.assertEqual(0.5, sim.nine[1])
        self.assertEqual(0, sim.seventeen[1])
        # third row
        self.assertEqual(0.25, sim.two[2])
        self.assertEqual(0.5, sim.six[2])
        self.assertEqual(1, sim.nine[2])
        self.assertEqual(0, sim.seventeen[2])
        # fourth row
        self.assertEqual(0, sim.two[3])
        self.assertEqual(0, sim.six[3])
        self.assertEqual(0, sim.nine[3])
        self.assertEqual(1, sim.seventeen[3])


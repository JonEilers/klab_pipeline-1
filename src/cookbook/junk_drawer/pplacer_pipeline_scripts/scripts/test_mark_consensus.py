import unittest

import mark_consensus

class UpdateMaskPositions(unittest.TestCase):

    def setUp(self):
        self.updated_consensus = [False, True, True, True, False, True, False,
                True]
        self.mask_positions = [1, 2, 5, 7]

    def test_all_in(self):
        mask_positions = [1, 2, 3, 5, 7]
        actual = mark_consensus.update_mask_positions(self.updated_consensus,
                mask_positions)
        self.assertEquals([0, 1, 2, 3, 4], actual)

    def test_mix(self):
        actual = mark_consensus.update_mask_positions(self.updated_consensus,
                self.mask_positions)

        self.assertEquals([0, 1, 3, 4], actual)

    def test_none_in(self):
        mask_positions = []
        actual = mark_consensus.update_mask_positions(self.updated_consensus,
                mask_positions)
        self.assertEquals([], actual)

    def test_invalid_mask(self):
        mask_positions = [len(self.updated_consensus)]
        self.assertRaises(IndexError, mark_consensus.update_mask_positions,
                self.updated_consensus, mask_positions)
        self.assertRaises(AssertionError, mark_consensus.update_mask_positions,
                self.updated_consensus, [0])

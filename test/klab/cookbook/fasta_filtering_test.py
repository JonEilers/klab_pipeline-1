import unittest

from cookbook.fasta_filtering import _lineage_contains, _turn_ncbi_name_into_file_name, _split_fasta_file


class TestFastaFiltering(unittest.TestCase):
    def test_lineage_contains(self):
        self.assertFalse(_lineage_contains([1, 131567, 2, 18, 19], {5}))
        self.assertTrue(_lineage_contains([1, 131567, 2, 18, 19], {2}))
        self.assertTrue(_lineage_contains([1, 131567, 2, 18, 19], {2, 5}))
        self.assertTrue(_lineage_contains([1, 131567, 2, 6, 7, 9], {2, 5}))

    def test_turn_ncbi_name_into_file_name(self):
        self.assertEqual('this_is_a-test_so_there', _turn_ncbi_name_into_file_name('This is/a-Test.so&There'))
        self.assertEqual('bacillus_sp_a21_2015', _turn_ncbi_name_into_file_name('Bacillus sp. A21(2015)'))
        self.assertEqual('influenza_a_virus_a_swine_south_dakota_a01481942_2014_h1n1',
                         _turn_ncbi_name_into_file_name(
                             'Influenza A virus (A/swine/South Dakota/A01481942/2014(H1N1))'))

    def test_split_fasta_file(self):
        try:
            _split_fasta_file(None, None, None, None)
            self.fail('should have thrown ValueError')
        except ValueError, ve:
            self.assertEqual('no_dir is not a directory.', ve.message)

        try:
            _split_fasta_file('no_file', None, None, None)
            self.fail('should have thrown ValueError')
        except ValueError, ve:
            self.assertEqual('no_file is not a file.', ve.message)

import unittest

import klab.processing.file_manager as file_manager


class TestFileManager(unittest.TestCase):
    def test_read_df_from_file(self):
        df = file_manager.read_df_from_file('/package_compare/test/data/test_data.tsv')
        self.assertEquals(7, len(df.index))
        self.assertEquals(9, len(df.columns))


    def test_build_data_frame_from_jplace_files(self):
        df = file_manager._build_data_frame_from_jplace_files('/package_compare/test/data')

        self.assertEquals(134, len(df.index))
        self.assertEquals(10, len(df.columns))

        self.assertEqual('.1-.8_coastal_FHGDIPM01D4PA5_4', df.fragment_id[0])
        self.assertEqual('COG0001', df.cluster[0])
        self.assertEqual('2', df.classification[0])
        self.assertAlmostEqual(0.087771, df.distal_length[0], 6)
        self.assertEqual(1043, df.edge_num[0])
        self.assertAlmostEqual(0.304988, df.like_weight_ratio[0], 6)
        self.assertAlmostEqual(-24551.096813, df.likelihood[0], 6)
        self.assertAlmostEqual(0.051685, df.marginal_like[0], 6)
        self.assertAlmostEqual(1.961135, df.pendant_length[0], 6)
        self.assertAlmostEqual(0.002871, df.post_prob[0], 6)

    def test_classification_data_type_issue(self):
        df = file_manager._build_data_frame_from_jplace_files('/package_compare/test/data')
        self.assertEqual('object', str(df[file_manager.CLASSIFICATION_COLUMN].dtypes))

        df2 = file_manager.create_placements('/package_compare/test/data')
        self.assertEqual('int64', str(df2[file_manager.CLASSIFICATION_COLUMN].dtypes))

    # TODO ech 2015-03-09 - implement this
    def test_prune_unwanted_rows(self):
        pass

    # TODO ech 2015-03-09 - implement this
    def test_fix_dup_problem_with_hack(self):
        pass

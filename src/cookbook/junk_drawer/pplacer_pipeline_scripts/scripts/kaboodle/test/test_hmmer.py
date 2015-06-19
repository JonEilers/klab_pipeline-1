import collections
import unittest

from kaboodle import hmmer

class ChooseBestHitTestCase(unittest.TestCase):
    def setUp(self):
        rec = collections.namedtuple('testrecord',
                ('target_name', 'dom_score', 'query_name',
                 'env_from', 'env_to'))
        self.records = [
                rec('seq1', 10.5, 'hmm1', 10, 25),
                rec('seq2', 10.5, 'hmm1', 10, 25),
                rec('seq3', 14.8, 'hmm3', 30, 35),
                rec('seq1', 5.0, 'hmm4', 30, 35),
                rec('seq3', 15.0, 'hmm5', 100, 154)]
        self.rec_iter = iter(self.records)

    def test_defaults(self):
        expected = [(0, 'seq1', 'hmm1',10, 25, 10.5),
                    (1, 'seq2', 'hmm1', 10, 25, 10.5),
                    (4, 'seq3', 'hmm5', 100, 154, 15.0)]
        actual, count = hmmer.choose_best_hit(self.rec_iter)
        self.assertEqual(len(self.records), count)
        self.assertEqual(expected, map(tuple, actual))

    def test_minimize(self):
        actual, count = hmmer.choose_best_hit(self.rec_iter, maximize=False)
        expected = [(1, 'seq2', 'hmm1', 10, 25, 10.5),
                    (2, 'seq3', 'hmm3', 30, 35, 14.8),
                    (3, 'seq1', 'hmm4', 30, 35, 5.0),]
        self.assertEqual(len(self.records), count)
        self.assertEqual(expected, actual)

class ExtractIndicesTestCase(unittest.TestCase):

    def setUp(self):
        self.iterable = 'abcdefgh'
        self.indices = [0, 1, 5]
        self.expected = ['a', 'b', 'f']

    def test_basic(self):
        actual = list(hmmer.extract_indices(self.iterable, self.indices))
        self.assertEqual(self.expected, actual)

    def test_size_correct(self):
        actual = list(hmmer.extract_indices(self.iterable, self.indices,
            len(self.iterable)))
        self.assertEqual(self.expected, actual)
    def test_size_incorrect(self):
        actual = hmmer.extract_indices(self.iterable, self.indices,
            len(self.iterable) - 1)
        self.assertRaises(ValueError, list, actual)

class SequencesByHmmTestCase(unittest.TestCase):

    def setUp(self):
        BestHit = collections.namedtuple('Seq', 'target_name query_name')

        self.best_hits = [BestHit('seq2', 'hmm3'),
                          BestHit('seq3', 'hmm3'), BestHit('seq1', 'hmm4')]

    def test_basic(self):
        result = [(g, list(v))
                  for g, v in hmmer.sequences_by_hmm(self.best_hits)]
        self.assertEqual([('hmm3', self.best_hits[:2]), ('hmm4', self.best_hits[2:])],
                result)

import pandas as pd

from klab.analysis.diversity import _build_lineage_dict, _calculate_similarity, _build_similarity_matrix, \
    build_similarity_frame, CLASSIFICATION_NAME_COLUMN
from klab.process import lineage
from klab.process.file_manager import CLASSIFICATION_COLUMN

node_dict = {
    1: (1, lineage.NO_RANK),  # root
    131567: (1, lineage.NO_RANK),  # cellular organisms
    2: (131567, 'superkingdom'),  # bacteria
    2759: (131567, 'superkingdom'),  # eukaryota
    6: (2, 'genus'),  # rest of these are bogus nodes
    7: (6, 'species'),
    9: (7, lineage.NO_RANK),
    17: (131567, lineage.NO_RANK),
    18: (2, lineage.NO_RANK),
    19: (18, lineage.NO_RANK),
    56: (9, 'variety'),
}


def test_calculate_similarity():
    placements = pd.DataFrame(node_dict.keys(), columns=[CLASSIFICATION_COLUMN])
    ld = _build_lineage_dict(node_dict, placements)

    delta = 0.00001
    assert abs(0.0 - _calculate_similarity(ld, -1, -2)) <= delta  # both not in lineage
    assert abs(0.0 - _calculate_similarity(ld, -1, 2)) <= delta  # one not in list
    assert abs(0.0 - _calculate_similarity(ld, 1, 2)) <= delta  # root gets pruned out
    assert abs(0.0 - _calculate_similarity(ld, 2, 2759)) <= delta  # no similarity between domains
    assert abs(0.0 - _calculate_similarity(ld, 56, 2759)) <= delta  # ditto
    assert abs(1.0 - _calculate_similarity(ld, 56, 56)) <= delta  # same item is always 1
    assert abs(1.0 - _calculate_similarity(ld, -1, -1)) <= delta  # still 1, even if not in lineage
    assert abs(0.5 - _calculate_similarity(ld, 2, 6)) <= delta
    assert abs(0.5 - _calculate_similarity(ld, 6, 2)) <= delta
    assert abs(0.33333 - _calculate_similarity(ld, 2, 7)) <= delta
    assert abs(0.25 - _calculate_similarity(ld, 2, 9)) <= delta
    assert abs(0.5 - _calculate_similarity(ld, 18, 6)) <= delta
    assert abs(0.5 - _calculate_similarity(ld, 6, 9)) <= delta
    assert abs(0.75 - _calculate_similarity(ld, 7, 9)) <= delta
    assert abs(0.8 - _calculate_similarity(ld, 56, 9)) <= delta


def test_build_similarity_matrix():
    dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
    abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
    sm, k = _build_similarity_matrix(node_dict, abundance)
    assert 4, len(k)
    # first row
    assert 1 == sm[0][0]
    assert 0.5 == sm[0][1]
    assert 0.25 == sm[0][2]
    assert 0 == sm[0][3]
    # second row
    assert 0.5 == sm[1][0]
    assert 1 == sm[1][1]
    assert 0.5 == sm[1][2]
    assert 0 == sm[1][3]
    # third row
    assert 0.25 == sm[2][0]
    assert 0.5 == sm[2][1]
    assert 1 == sm[2][2]
    assert 0 == sm[2][3]
    # fourth row
    assert 0 == sm[3][0]
    assert 0 == sm[3][1]
    assert 0 == sm[3][2]
    assert 1 == sm[3][3]


def test_build_lineage_dict():
    dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
    abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
    ld = _build_lineage_dict(node_dict, abundance)
    assert [2, 6, 9, 17] == sorted(ld.keys())
    assert [2] == ld.get(2)
    assert [2, 6] == ld.get(6)
    assert [2, 6, 7, 9] == ld.get(9)
    assert [17] == ld.get(17)


def test_build_similarity_frame():
    dat = [[2, 'two', 4], [6, 'six', 5], [9, 'nine', 2], [17, 'seventeen', 25]]
    abundance = pd.DataFrame(data=dat, columns=[CLASSIFICATION_COLUMN, CLASSIFICATION_NAME_COLUMN, 'count'])
    sim = build_similarity_frame(abundance, node_dict)

    assert 4 == len(sim.index)
    assert ['two', 'six', 'nine', 'seventeen'] == list(sim.columns)
    # first row
    assert 1 == sim.two[0]
    assert 0.5 == sim.six[0]
    assert 0.25 == sim.nine[0]
    assert 0 == sim.seventeen[0]
    # second row
    assert 0.5 == sim.two[1]
    assert 1 == sim.six[1]
    assert 0.5 == sim.nine[1]
    assert 0 == sim.seventeen[1]
    # third row
    assert 0.25 == sim.two[2]
    assert 0.5 == sim.six[2]
    assert 1 == sim.nine[2]
    assert 0 == sim.seventeen[2]
    # fourth row
    assert 0 == sim.two[3]
    assert 0 == sim.six[3]
    assert 0 == sim.nine[3]
    assert 1 == sim.seventeen[3]

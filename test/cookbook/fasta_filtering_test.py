# TODO ech 2016-11-17 - figure out why it can't find fasta_filtering
import pytest

from cookbook.fasta_filtering import _lineage_contains, _turn_ncbi_name_into_file_name, _split_fasta_file


def test_lineage_contains():
    assert not _lineage_contains([1, 131567, 2, 18, 19], {5})
    assert _lineage_contains([1, 131567, 2, 18, 19], {2})
    assert _lineage_contains([1, 131567, 2, 18, 19], {2, 5})
    assert _lineage_contains([1, 131567, 2, 6, 7, 9], {2, 5})


def test_turn_ncbi_name_into_file_name():
    assert 'this_is_a-test_so_there' == _turn_ncbi_name_into_file_name('This is/a-Test.so&There')
    assert 'bacillus_sp_a21_2015' == _turn_ncbi_name_into_file_name('Bacillus sp. A21(2015)')
    assert 'influenza_a_virus_a_swine_south_dakota_a01481942_2014_h1n1' == \
           _turn_ncbi_name_into_file_name('Influenza A virus (A/swine/South Dakota/A01481942/2014(H1N1))')


def test_split_fasta_file():
    with pytest.raises(ValueError) as ve:
        _split_fasta_file('no_file', None, None, None)
    assert 'no_file is not a file.' in str(ve.value)

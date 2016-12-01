#!/usr/bin/env python

from __future__ import unicode_literals

import os

import pytest

from klab.jplace.jplace_filter import filter_jplace_files
from process.file_manager_test import DATA_DIR
from process.lineage_test import node_dict, name_dict


def test_filter_jplace_file():
    with pytest.raises(RuntimeError) as re:
        filter_jplace_files(files=None, output_dir=None, filter_items=['bad taxa name'], node_dict=node_dict,
                            name_dict=name_dict)
    assert 'is not a NCBI taxa name' in str(re.value)

    with pytest.raises(RuntimeError) as re:
        filter_jplace_files(files=None, output_dir=None, filter_items=[4], node_dict=node_dict,
                            name_dict=name_dict)
    assert 'is not a NCBI taxa id' in str(re.value)

    files = [os.path.join(DATA_DIR, 'PHA0198.aln/PHA0198.aln.aligned.jplace')]
    filter_jplace_files(files=files, output_dir='/tmp', filter_items=['Bacteria'],
                        node_dict=node_dict, name_dict=name_dict)

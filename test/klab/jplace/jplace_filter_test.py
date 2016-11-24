#!/usr/bin/env python

from __future__ import unicode_literals

import os

import pytest

from klab.jplace.jplace_filter import filter_jplace_files
from process.file_manager_test import DATA_DIR
from process.lineage_test import node_dict, name_dict


def test_filter_jplace_file():
    with pytest.raises(ValueError):
        filter_jplace_files(files=None, output_dir=None, filter_names=['bad taxa name'], node_dict=node_dict,
                            name_dict=name_dict)

    files = [os.path.join(DATA_DIR, 'PHA0198.aln/PHA0198.aln.aligned.jplace')]
    filter_jplace_files(files=files, output_dir='/tmp', filter_names=['Bacteria'],
                        node_dict=node_dict, name_dict=name_dict)

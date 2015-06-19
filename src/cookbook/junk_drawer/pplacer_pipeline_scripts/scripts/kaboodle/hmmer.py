#!/usr/bin/env python
"""
Run an hmmsearch against a set of reference packages, build infrastructure for
pplacer analysis
"""

import collections
import itertools
import logging
import operator
import os
import os.path
import re
import shutil
import subprocess
import tempfile

from Bio import SeqIO

LINE_LENGTH = 23
HEADERS = ['target_name', 'target_accession', 'tlen', 'query_name',
    'accession', 'qlen', 'e_value', 'score', 'bias', 'number', 'of',
    'dom_c_evalue', 'dom_i_evalue', 'dom_score', 'dom_bias', 'dom_from', 'dom_to',
    'ali_from', 'ali_to', 'env_from', 'env_to', 'env_acc', 'description']
CONVERTERS = {'dom_score': float, 'env_from': int, 'env_to': int}
WHITESPACE_RE = re.compile(r'\s+')
assert len(HEADERS) == LINE_LENGTH, len(HEADERS)

DomtblRecord = collections.namedtuple('DomtblRecord', HEADERS)

def _domtbl_split(line):
    """Split a single line of the dom table"""
    result = [i.strip() for i in WHITESPACE_RE.split(line,
                                                     maxsplit=LINE_LENGTH - 1)]
    assert len(result) == LINE_LENGTH
    return result

def domtbl_parse(fp):
    """
    Parse the --domtblout of an hmmsearch
    yields row dictionaries
    """
    lines = (i for i in fp if not i.startswith('#'))
    records = (dict(zip(HEADERS, _domtbl_split(line))) for line in lines)
    for record in records:
        for k in CONVERTERS:
            if k in record:
                try:
                    record[k] = CONVERTERS[k](record[k])
                except ValueError:
                    # Allow parse failures
                    pass
        yield DomtblRecord(**record)

def cat(paths, output_fp):
    """
    Copy contents of all files in paths to output_fp
    """
    for p in paths:
        with open(p, 'rb') as fp:
            shutil.copyfileobj(fp, output_fp)

def hmm_name(fp):
    """
    Gets the name of an HMM
    """
    try:
        header = next(fp)
    except StopIteration:
        raise IOError("no lines found in {0}".format(fp))

    if not header.startswith('HMMER3'):
        raise IOError("""Unexpected first line. Is this an HMM?\n{0}""".format(header))
    for line in fp:
        if line.startswith('NAME'):
            return line[5:].strip()
    raise IOError("no NAME record found in {0}".format(fp))

def hmmsearch(hmm_file, seq_file, max_e_value='1e-5', domtblout=None,
        output=None, mpi_command=None, align_file=None):
    """
    Run hmmsearch
    """
    opts = []
    for k in ('-E', '--incE', '--incdomE', '--domE'):
        opts.extend((k, str(max_e_value)))
    if domtblout:
        opts.extend(('--domtblout', domtblout))
    opts.extend(('-o', output or os.devnull))
    if align_file:
        opts.extend(('-A', align_file))

    command = ['hmmsearch'] + opts + [hmm_file, seq_file]
    if mpi_command:
        command = [mpi_command] + command[0:1] +  ['--mpi'] + command[1:]
    logging.info(' '.join(command))
    subprocess.check_call(command)
    logging.info('Finished: %s', ' '.join(command))

def choose_best_hit(domtbl_records, method='dom_score', maximize=True):
    """
    Given a set of domtbl_records, return the record indexes of the best-scoring
    hits.
    Returns list of (index, name, query, score) tuples, count
    """
    BestHit = collections.namedtuple('BestHit',
            ['index', 'target_name', 'query_name', 'env_from', 'env_to',
             method])
    if maximize:
        better = lambda a, b: a > b
    else:
        better = lambda a, b: a < b

    # target_name -> (index, query, val)
    result = {}
    for i, record in enumerate(domtbl_records):
        old_rec = result.get(record.target_name, None)
        cur_val = getattr(record, method)
        if old_rec is None or better(cur_val, getattr(old_rec, method)):
            result[record.target_name] = BestHit(i, record.target_name,
                   record.query_name, record.env_from, record.env_to,
                   cur_val)

    count = i + 1

    result = sorted(result.values(), key=operator.attrgetter('index'))
    return result, count

class IndexedSequenceFetcher(object):
    """
    Extract sequences from a sequence file using Biopython's index_db
    """
    def __init__(self, sequence_file_path, fmt='fasta'):
        self.index_path = sequence_file_path + '.index'
        if not os.path.exists(self.index_path):
            logging.warn('No index exists - one will be created at %s. '
                    'This may take a few minutes.',
                    self.index_path)

        self.index_db = SeqIO.index_db(self.index_path, sequence_file_path,
                fmt)

    def __getitem__(self, key):
        try:
            return self.index_db[key]
        except KeyError:
            raise KeyError(str(key))

    def extract_best_hits(self, best_hits):
        """
        Extract sequences cut to a region from best_hits
        """
        for hit in best_hits:
            sequence = self[hit.target_name]
            # Slice to coordinates
            # Results are 1-based
            yield sequence[hit.env_from - 1:hit.env_to]

def extract_indices(iterable, indices, expected_size=None):
    """
    Extract all elements of iterable whose index is contained in indices.

    If expected_size is specified, throw an exception if a different number of
    items are processed
    """
    indices = frozenset(indices)
    for i, j in enumerate(iterable):
        if i in indices:
            yield j
    if expected_size is not None and i+1 != expected_size:
        raise ValueError('Unexpected number of records: {0} != {1}'.format(
            expected_size, i + 1))

def sequences_by_hmm(best_hits):
    """
    Returns grouped (hmm_name, best_hits)
    """
    # Group by query_name
    grouped = itertools.groupby(best_hits, lambda i: i.query_name)
    return grouped

def recruit_sequences(hmm_path, sequence_file, domtblout, max_e_value,
                      mpi_command):
    """
    Recruit sequences to HMMs. Yields hmm_name, SeqRecords pairs
    """
    # Hmmsearch
    hmmsearch(hmm_path, sequence_file,
              domtblout=domtblout,
              max_e_value=max_e_value,
              mpi_command=mpi_command)

    # Parse results
    with open(domtblout) as fp:
        results = domtbl_parse(fp)
        best_hits, dom_hit_count = choose_best_hit(results)

    logging.info("%d hits to HMMs", dom_hit_count)
    logging.info("Chose %d best hits", len(best_hits))

    return sequences_by_hmm(best_hits)

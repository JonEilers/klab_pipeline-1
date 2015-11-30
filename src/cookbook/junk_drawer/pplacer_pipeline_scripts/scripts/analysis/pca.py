#!/usr/bin/env python
"""
Run guppy PCA on samples
"""

import csv
import json
import os.path
import subprocess

from Bio import SeqIO

dn = os.path.dirname(__file__)


def main():
    with open('control.json') as fp:
        d = json.load(fp)
    jplace = d['title'] + '.aligned.jplace'
    sample_map = d['title'] + '.mapping.csv'
    recruit = 'recruit.fasta'
    recruit_ids = (s.id for s in SeqIO.parse(recruit, 'fasta'))
    csv_tuples = ((i, i.split('_')[1].replace('costal', 'coastal'))
                  for i in recruit_ids)
    with open(sample_map, 'w') as fp:
        writer = csv.writer(fp, quoting=csv.QUOTE_NONE)
        writer.writerows(csv_tuples)

    # Run PCA
    pca_base = d['title'] + '_pca'
    cmd = ['guppy', 'pca', '--prefix', pca_base,
           ':'.join((jplace, sample_map))]
    print ' '.join(cmd)
    subprocess.check_call(cmd)

    r_script = os.path.join(dn, 'pca_plot.R')
    cmd = ['Rscript', r_script, pca_base + '.trans', d['title']]
    subprocess.check_call(cmd)


if __name__ == '__main__':
    main()

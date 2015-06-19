#!/usr/bin/env python

import csv
import json
import os.path
import subprocess
import tempfile

from Bio import SeqIO

comps = [('surface', 'DCM'), ('coastal', 'upwelling')]

def parse_ids(file_name='recruit.fasta'):
    recruit_ids = (s.id for s in SeqIO.parse(file_name, 'fasta'))
    csv_tuples = ((i, i.split('_')[1].replace('costal', 'coastal'))
                  for i in recruit_ids)
    return list(csv_tuples)


def kr_heat(placefile, id_map, sample1, sample2, outfile):
    with tempfile.NamedTemporaryFile(suffix='.csv') as ntf:
        writer = csv.writer(ntf, quoting=csv.QUOTE_MINIMAL, lineterminator='\n')
        writer.writerows((i, j) for i, j in id_map if j in (sample1, sample2))
        ntf.flush()

        cmd = ['guppy', 'kr_heat', '-o', outfile, ':'.join((placefile, ntf.name))]
        print ' '.join(cmd)
        subprocess.check_call(cmd)

def main():
    with open('control.json') as fp:
        control = json.load(fp)
    jplace = control['title'] + '.aligned.jplace'
    assert os.path.exists(jplace)
    ids = parse_ids()
    for sample1, sample2 in comps:
        outfile = '{0}_kr_{1}_{2}.xml'.format(control['title'],
                sample1, sample2)
        kr_heat(jplace, ids, sample1, sample2, outfile)

if __name__ == '__main__':
    main()

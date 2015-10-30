#!/usr/bin/env python

import argparse
import subprocess

from klab.process.file_manager import get_files

"""
Calculates Expected Distance between Placement Locations using pplacer guppy utility.

Inspired by Ryan's EDPL_calc.py
"""


def calculate_edpl(out_file, dir):
    jplace_file_list = get_files(dir)

    print ('%d files to run...' % len(jplace_file_list))

    edpl_list = []
    for jplace in jplace_file_list:
        print ('processing %s...' % jplace)

        if jplace.split('.')[-1] == 'jplace':
            gene = jplace.split('.')[0]
            edpl_out = subprocess.check_output(['guppy', 'edpl', jplace], stderr=subprocess.STDOUT)
            for edpl in edpl_out.split('\n'):
                if edpl.replace(' ', '') != '':
                    edpl_list.append(gene + ',' + ','.join(filter(None, edpl.split(' '))))
    output = open(out_file, 'w')
    output.write('\n'.join(edpl_list))
    output.close()


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-directory', help='directory with .jplace files', required=True)
    parser.add_argument('-out_file', help='output file', required=True)
    args = parser.parse_args()

    calculate_edpl(dir=args.directory, out_file=args.out_file)

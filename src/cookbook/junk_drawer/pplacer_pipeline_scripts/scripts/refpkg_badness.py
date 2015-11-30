#!/home/mclaugr4/software/bin/python
"""
Aggregate the badness of a set of reference packages at a given rank
"""
import argparse
import collections
import csv
import os.path
import subprocess
import sys


def refpkg_info(path):
    print >> sys.stderr, path
    bn = os.path.splitext(os.path.basename(path))[0]
    cmd = ['rppr', 'info', '-c', path, '--csv']
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    reader = csv.DictReader(p.stdout)
    try:
        l = list(reader)
        for i in l:
            i['refpkg'] = bn
        return {i['rank']: i for i in l}
    finally:
        p.wait()
        assert p.returncode == 0


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rank', dest='ranks', nargs='+', default=['phylum', 'family'], help="Rank to show badness")
    parser.add_argument('refpkgs', metavar='refpkg', nargs='+', help="Reference package path")
    a = parser.parse_args()

    results = (refpkg_info(i).get(rank, collections.defaultdict(lambda: None)) for i in a.refpkgs
               for rank in a.ranks)
    writer = csv.DictWriter(sys.stdout, ('refpkg', 'rank', 'n_taxids', 'n_nonconvex', 'max_bad', 'tot_bad'),
                            extrasaction='ignore')
    writer.writeheader()
    writer.writerows(results)


if __name__ == '__main__':
    main()

#!/home/mclaugr4/software/bin/python

import argparse

from taxtastic import refpkg

def update_refpkg(p):
    r = refpkg.Refpkg(p)
    r.update_phylo_model(None, r.file_abspath('tree_stats'))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('refpkgs', metavar='refpkg', nargs='+')
    args = parser.parse_args()

    for r in args.refpkgs:
        print r
        update_refpkg(r)

if __name__ == '__main__':
    main()

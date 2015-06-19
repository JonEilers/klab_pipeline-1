#!/home/mclaugr4/software/bin/python
"""
Fix reference packages containing incorrect rank-order taxtables,
specifically parvorder / infraorder inversions.
"""
import argparse
import csv
import os.path
import re
import sys
import tempfile

from taxtastic import refpkg
from taxtastic.ncbi import ranks

TAX_KEY = 'taxonomy'
RANK_ORDER = {rank: i for i, rank in enumerate(ranks)}

def sort_rank_headers(rank_headers, prefix="below"):
    """
    Sort rank order based on NCBI taxonomy.
    """
    def to_tuple(header):
        prefix_count = header.count(prefix)
        header_stripped = re.sub(r'({0}_)*(.*$)'.format(prefix), r'\2', header)
        return header_stripped, prefix_count

    keys = {header: to_tuple(header) for header in rank_headers}
    return sorted(rank_headers,
                  key=lambda h: (RANK_ORDER[keys[h][0]], keys[h][1]))

def update_refpkg(path):
    """
    Fix rank order within reference package
    """
    rpkg = refpkg.Refpkg(path)
    assert not rpkg.is_invalid()

    current_taxonomy = rpkg.file_abspath(TAX_KEY)

    with open(current_taxonomy) as fp:
        reader = csv.DictReader(fp)

        # Fix header order
        base_headers = reader.fieldnames[:4]
        rank_headers = reader.fieldnames[4:]
        reordered = sort_rank_headers(rank_headers)
        assert len(reordered) == len(reordered)

        if reordered == rank_headers:
            # No update needed
            return False

        with tempfile.NamedTemporaryFile(prefix=os.path.basename(current_taxonomy)) as tf:
            writer = csv.DictWriter(tf, base_headers + reordered,
                    quoting=csv.QUOTE_NONNUMERIC)
            writer.writeheader()
            writer.writerows(reader)

            # No need to delete
            tf.delete = False

        rpkg.update_file(TAX_KEY, tf.name)

        return True

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('refpkgs', metavar='refpkg', help="""Reference package
            directory""", nargs="+")
    arguments = parser.parse_args()
    writer = csv.writer(sys.stdout, delimiter='\t')
    writer.writerow(('refpkg', 'updated?'))
    for r in arguments.refpkgs:
        result = update_refpkg(r)
        writer.writerow((r, result))

if __name__ == '__main__':
    main()

import os
import sys
import subprocess
import argparse

from cookbook.junk_drawer.support.DAP_DATA_PROC import jplaceDDP


def main(outfile, jdir):
    # jplace_file_list = os.listdir(jplace_path)
    jplace_file_list = []
    # If user specifies a file directory for the input .jplace files
    for root, dirs, files in os.walk(jdir, topdown=True):
        if root[-1] != '/':
            root += '/'
        for f in files:
            if f.split('.')[-1].find('jplace') != -1:
                # Checks to see if jplace have placements
                if jplaceDDP(root + f).emptyjplace():
                    jplace_file_list.append(root + f)
                else:
                    print (f, 'has no placements...')

    print (len(jplace_file_list), 'files to run...')

    edpl_list = []
    for jplace in jplace_file_list:
        if jplace.split('.')[-1] == 'jplace':
            gene = jplace.split('.')[0]
            edpl_out = subprocess.check_output(['guppy', 'edpl', jplace], stderr=subprocess.STDOUT)
            out_list = edpl_out.split('\n')
            for edpl in out_list:
                if edpl.replace(' ', '') != '':
                    edpl_list.append(gene + ',' + ','.join(filter(None, edpl.split(' '))))
            print (jplace, 'has been processed...')
    output = open(outfile, 'w')
    output.write('\n'.join(edpl_list))
    output.close()


if __name__ == '__main__':
    # collect arguments from commandline
    parser = argparse.ArgumentParser(description='Welcome to EDPL Calc! Get your jplace files ready for processing!')
    parser.add_argument('-o', '--outfile', help='outputfile', required=True)
    parser.add_argument('-d', '--jdir', help='path to input jplace directory.', required=True)
    args = vars(parser.parse_args())
    # check to make sure that enough arguments were passed before proceeding
    if len(sys.argv) < 2:
        sys.exit("Missing flags, type \"--help\" for assistance...")
    main(args['outfile'], args['jdir'])

#!/bin/bash

#
# Grabs us some data from the interwebs
#

# Constants
TAXONOMY_FILE="taxdump.tar.gz"
NCBI_SITE="ftp.ncbi.nih.gov/pub/taxonomy"
GOOD_ROW_MARKER="scientific"
DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd ) # dir where this script lives

cd $DIR

# if end file already exists, then don't need to do anything
if [ -f names.tsv ]; then
	# echo "NCBI files already exist, skipping download."
	exit 0;
fi

# download zipped file and extract the goodies
wget ftp://$NCBI_SITE/$TAXONOMY_FILE
tar -xzf $TAXONOMY_FILE nodes.dmp names.dmp merged.dmp delnodes.dmp readme.txt
mv readme.txt ncbi_readme.txt
rm -f $TAXONOMY_FILE

# *.dmp files are bcp-like dump format from GenBank taxonomy database
# Field terminator is "\t|\t"
# Row terminator is "\t|\n"

# names file
# parse out the useful rows
grep $GOOD_ROW_MARKER names.dmp > temp.dmp
# keep the tax_id and name columns
cat temp.dmp | cut -f1,3 > names.tsv # second column is '|' from dmp field terminator

# nodes file
# keep the tax_id and parent columns
cat nodes.dmp | cut -f1,3 > nodes.tsv

# merged nodes file
# keep the old and new columns
cat merged.dmp | cut -f1,3 > merged.tsv

# deleted nodes file
# trim off trailing separator
cat delnodes.dmp | cut -f1 > delnodes.tsv

# clean up working files
rm -f *.dmp

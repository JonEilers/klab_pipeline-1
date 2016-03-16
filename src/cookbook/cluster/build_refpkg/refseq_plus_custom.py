#!/usr/bin/env python
"""Download refseq data sets
"""
# $REV$
# $DATE$
# 
# --------------------------------------------------------------------------- #
# Center for Environmental Genomics
# Copyright (C) 2009 University of Washington.  All Rights Reserved.
#            
# Authors:
# Chris Berthiaume
# chrisbee@u.washington.edu
# --------------------------------------------------------------------------- #
import os
import sys
import re
from optparse import OptionParser
import urllib2
import tempfile
import shutil
from Bio import SeqIO

# Define global variables
ftp_url = "ftp://ftp.ncbi.nih.gov/refseq/release/"
version_url = ftp_url + "release-notes/"
version_base = "RefSeq-release"
file_ending = "*.protein.faa.gz" # file ending for refseq protein parts

def option():
    usage = "usage: %prog local_fasta refseq_part1 [refseq_part2 ...]\n\n"
    usage += "Download refseq protein subsections (fungi, plastid, etc.),\n"
    usage += "concatenate them, reduce headers to ID part with taxonomy,\n"
    usage += "deduplicate by sequence ID.  Finally, combine this aggregated\n"
    usage += "refseq fasta file with a local fasta file.\n"
    parser = OptionParser(usage)
    parser.add_option("--taxid", "-t", default=False, action="store_true",
                      help="Add tax ID to start of seq ID [%default]")
    parser.add_option("--no_dl", default=False, action="store_true",
                      help="Don't download, assume files already present [%default]")
    (option, args) = parser.parse_args()
    
    # Check that the minimum number of arguments was given
    if len(args) < 2:
        sys.stderr.write("At least 2 arguments are required\n")
        parser.print_help()
        sys.exit(1)
    # Change local fasta to absolute path and validate existence
    if args[0]:
        args[0] = os.path.abspath(args[0])
        if not os.path.isfile(args[0]):
            sys.stderr.write("%s is not a valid file\n" % args[0])
            sys.exit(1)
    # Check for validity of refseq subsection names
    for section in args[1:]:
        try:
            section_url = ftp_url + section
            ftp = urllib2.build_opener(urllib2.FTPHandler).open(section_url)
            print "found refseq subsection %s" % section
        except:
            sys.stderr.write("%s is not a valid refseq subsection\n" % section)
            sys.exit(1)
    print
    return (option, args)

def make_gi2taxid(refseq_release, gi_taxid_file):
    """Create a dictionary of refseq GI to taxon ID lookups as integers.
    
    The GI to taxonomic ID mapping can be found in 
    ftp://ftp.ncbi.nih.gov/refseq/release/release-catalog/RefSeq-release*.catalog.gz
    """
    # dictionary of key=gi (int), value=taxon ID (int)
    gi2taxid = dict()
    for line in open(gi_taxid_file, "r"):
        cols = line.rstrip().split("\t")
        gi2taxid[int(cols[3])] = int(cols[0])
    return gi2taxid
    
def fasta_prepend_taxid(records, gi2taxid, gi_col=2):
    """
    Fasta sequence iterator that prepends taxon IDs for sequences with GI
    numbers.  The original sequence is separated from the taxonomic ID by a 
    "|".
    
    gi_col = column position of GI number, where counting starts at 0
             and columns are separated by "|".
    """
    # look through fasta file, prepend taxonomic IDs to ID lines
    for r in records:
        gi = int(r.id.split("|")[gi_col])
        # Some GI => taxid associations aren't in the NCBI 
        # gi_taxid_[prot|nucl].dmp file.  Skip these sequences.
        if gi in gi2taxid:
            r.id = "%i|%s" % (gi2taxid[gi], r.id)
            r.description = ""
            yield r
        else:
            sys.stderr.write("GI %i not in map\n" % gi)
            #sys.exit() # commented out by Ryan 07/15/14

def refseq_addtaxa(records):
    """Add taxonomic information to protein ids for refseq based on information
    in fasta entry description. If there is one taxon for a sequence, this is
    added in hard brackets at the end of the identifier, no space between the
    identifier and [, and spaces are replaced with underscores.  If there are
    more than one taxa for a sequence, the first taxon is used as above and
    there is a + after the closing bracket.
    
    """
    # define the regular expression to find taxa description
    taxa_re = re.compile("\[[^\]]+\]")
    space_re = re.compile("\s+")
    for r in records:
        taxa = taxa_re.findall(r.description.split(None, 1)[1])
        if len(taxa):
            # Add taxa to ID with spaces replaced with _
            r.id = "%s%s" % (r.id, space_re.sub("_", taxa[0]))
            if len(taxa) > 1:
                # if there are more than one taxa, indicate with +
                r.id += "+"
            r.description = ""
        yield r

def prepend_text(records, prepend_text):
    """Fasta iterator which prepends text to each fasta sequence ID."""
    for r in records:
        r.id = "%s%s" % (prepend_text, r.id)
        desc = r.description.split(None, 1)
        if len(desc) > 1:
            r.description = desc[1]
        yield r

def main(local_fasta, refseq_parts, taxid=False, no_dl=False):
    # Get the refseq release version number
    ftp = urllib2.build_opener(urllib2.FTPHandler).open(version_url)
    version = [i for i in ftp if version_base in i][0].rstrip().split().pop()
    version = version[len(version_base):version.rfind(".txt")]
    
    # make a download directory in current working dir and chdir to it
    #downdir = tempfile.mkdtemp(dir=os.getcwd())
    downdir = "dl"
    try:
        os.mkdir(downdir)
    except OSError:
        pass
    os.chdir(downdir)
    
    if not no_dl:
        # Download all files for each refseq section
        for section in refseq_parts:
            file_glob = ftp_url + section + "/" + section + file_ending
            os.system("wget " + file_glob)
    
    # Construct the refseq output file name
    refseq_fasta = "refseq_protein." + version + "." + "_".join([i[:5] for i in refseq_parts]) + ".fa"
        
    # Concatenate unzipped fasta files
    try:
        os.remove(refseq_fasta)
    except OSError:
        pass
    for gz in [i for i in os.listdir('.') if i.endswith(".gz")]:
        os.system("gzip -d -c %s >>%s" % (gz, refseq_fasta))
    
    gi_taxid_file = "RefSeq-release%s.catalog.gz" % (version)
    if not no_dl:
        # Download the latest gi_taxid mapping file
        ncbi_ftp = "ftp://ftp.ncbi.nih.gov/refseq/release/release-catalog/"
        status = os.system("wget %s/%s" % (ncbi_ftp, gi_taxid_file))
        if status:
            sys.stderr.write("Download of %s failed\n" % gi_taxid_file)
            sys.exit(status)
        status = os.system("gunzip -f %s" % gi_taxid_file)
        if status:
            sys.stderr.write("Uncompress %s failed\n" % gi_taxid_file)
            sys.exit(status)
    gi_taxid_file = os.path.splitext(gi_taxid_file)[0]
    
    gi2taxid = make_gi2taxid(version, gi_taxid_file)
    sys.stderr.write("finished creating GI -> tax ID mapping\n")
    #os.remove(gi_taxid_file)
    
    sys.stderr.write("gi2taxid lookup table created\n")
    out_fasta = os.path.splitext(refseq_fasta)[0] + ".tax.fasta"
    seqin = SeqIO.parse(open(refseq_fasta), "fasta")
    out_handle = open(out_fasta, "w")
    file_prepend = os.path.basename(os.path.splitext(refseq_fasta)[0]) + "|"
    seqout_iter = refseq_addtaxa(prepend_text(seqin, file_prepend))
    if taxid:
        try: # added by Ryan 07/15/2014
            SeqIO.write(fasta_prepend_taxid(seqout_iter, gi2taxid), out_handle, "fasta")
        except: # added by Ryan 07/15/2014
            #print '#########################',seqout_iter,gi2taxid # added by Ryan 07/15/2014
            1+1
    else:
        SeqIO.write(seqout_iter, out_handle, "fasta")
    out_handle.close()
    
    # Concatenate refseq fasta file and local fasta file
    sys.stderr.write("Final concatenation step\n")
    if local_fasta:
        final_fasta = os.path.splitext(out_fasta)[0] +  ".plusCustom.fasta"
        os.system("cat %s %s >../%s" % (out_fasta, local_fasta, final_fasta))
    else:
        os.system("mv %s ../%s" % (out_fasta, out_fasta))
    os.chdir("..")
    return 0

if __name__ == "__main__":
    option, args = option()
    os.system("sleep 5") # pause before wget swamps terminal
    main(args[0], args[1:], option.taxid, option.no_dl)

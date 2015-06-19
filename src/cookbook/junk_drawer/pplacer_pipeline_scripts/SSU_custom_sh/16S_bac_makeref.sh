#!/bin/bash

#$ -S /bin/bash
#$ -cwd
#$ -N mk.16S_bac
#$ -e makeref.err
#$ -o makeref.out

### hmm_len() {{
###     local result=$(grep "^LENG" $1 | awk '{{ print $2 }}')
###     echo $result
### }}


EVALUE=1e-5
PDCUTOFF=1e-2
TAXDB=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/make_reference_packages/ncbi_taxonomy.db
EUKTAXIDREX=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/make_reference_packages/update_euk_taxid_regex.txt
LEN_THRESHOLD=0.2

RECRUITED=16S_bac.recruited
COMPLETE=16S_bac.complete
AUTO1=16S_bac.auto1
REF=16S_bac.ref

SCRIPTS=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/scripts

REMOVE_SHORT=$SCRIPTS/remove_short_seqs.py
TAXIDSOFFASTA=$SCRIPTS/taxids_of_fasta.py
MARKCONSENSUS=$SCRIPTS/mark_consensus.py
SM=/home/mclaugr4/software/bin/seqmagick

# Unalign, deduplicate taxa
### $SM convert --deduplicate-taxa recruit.fasta $RECRUITED.fasta
### $SM mogrify --dash-gap --ungap --first-name $RECRUITED.fasta

# Clean up names
### $SM mogrify --pattern-replace '[\[\]\(\),;:"+]' '' $RECRUITED.fasta
### $SM mogrify --pattern-replace "'" '' $RECRUITED.fasta
$SM mogrify --pattern-replace '[\[\]\(\),;:"+]' '' $COMPLETE.fasta
$SM mogrify --pattern-replace "'" '' $COMPLETE.fasta

# A little hack find the minimum ungapped legnth relative to the 
# length of the HMM. We want to include sequences who's ungapped length is
# < $LEN_THRESHOLD*HMM_LENGTH
### MIN_UNGAPPED_LEN=$(python -c "print int($(hmm_len {seed_hmm})*$LEN_THRESHOLD)")

### $SM convert --min-ungapped-length $MIN_UNGAPPED_LEN $RECRUITED.fasta \
###  $RECRUITED.tidy.fasta

# Generate an MSA from the sequences
### muscle3.8.31_i86linux64 -quiet -in $RECRUITED.tidy.fasta -out $COMPLETE.fasta

# Trimming and Deduplication
# Trimal generates a mask (.pre.mask) relative to position in the alignment.
# Below, we update to be relative to consensus columns in the stockholm
# file for the final mask
trimal -automated1 -colnumbering -in $COMPLETE.fasta -out $AUTO1.pre_subset.afa > 16S_bac.pre.mask
trimal -resoverlap 0.5 -seqoverlap 50 -in $AUTO1.pre_subset.afa \
  -out $AUTO1.afa
$SM convert --first-name --deduplicate-sequences --input-format fasta \
  $AUTO1.afa $AUTO1.dedup.fasta

 
# Pruning
### FastTree -nt -gtr -quiet $AUTO1.dedup.fasta > $AUTO1.fast.tre
FastTree -nt -gtr -quiet $COMPLETE.fasta > $AUTO1.fast.tre
rppr pdprune --cutoff $PDCUTOFF \
 --names-only -o $AUTO1.to_exclude $AUTO1.fast.tre
### rppr pdprune --never-prune-regex-from $EUKTAXIDREX --cutoff $PDCUTOFF \
###  --names-only -o $AUTO1.to_exclude $AUTO1.fast.tre
### $SM convert --exclude-from-file $AUTO1.to_exclude \
###  $AUTO1.dedup.fasta $AUTO1.pruned.fasta
$SM convert --exclude-from-file $AUTO1.to_exclude \
 $COMPLETE.fasta $AUTO1.pruned.fasta


# ref fasta, sto, and hmm
$SM extract-ids $AUTO1.pruned.fasta -o $AUTO1.pruned.ids
### $SM extract-ids $COMPLETE.fasta -o $AUTO1.pruned.ids

######################################################################
# Build a new stockholm file, containing only pruned sequences, with a
# consensus consisting of the union of consensus columns and unmasked
# positions
$SM convert --include-from-file $AUTO1.pruned.ids \
  $COMPLETE.fasta $COMPLETE.pruned.fasta

# use mark_consensus.py to generate a $COMPLETE.sto which has the
# mask-included sites as consensus columns
$MARKCONSENSUS $COMPLETE.pruned.fasta 16S_bac.pre.mask 16S_bac.mask \
  --stockholm-out $COMPLETE.sto --masked-out $REF.fasta
rm -f 16S_bac.pre.mask

# Convert pruned fasta to a stockholm
# added by Ryan to skip over the masking steps [09/15/2014]
$SM convert $COMPLETE.pruned.fasta $COMPLETE.sto
cp $COMPLETE.pruned.fasta $REF.fasta

hmmbuild --dna $COMPLETE.hmm $COMPLETE.sto

# make reference tree
### case "{tree_method}" in 
###   fasttree)
    ### FastTree -log $REF.stats -wag -gamma $REF.fasta > $REF.tre
FastTree -log $REF.stats -nt -gtr -gamma $REF.fasta > $REF.tre
STATS=$REF.stats
TREE=$REF.tre
###     ;;
###   raxml)
#fasta2phyml $REF.fasta
#raxmlHPC-PTHREADS-SSE3 -T 2 -m GTRGAMMA -n 16S_bac -s $REF.phymlAln
#STATS=RAxML_info.16S_bac
#TREE=RAxML_result.16S_bac
###     ;;
###   *)
###     echo "Unknown tree: {tree_method}"
###     exit 1
### esac    

# make refpkg!
$TAXIDSOFFASTA $REF.fasta
/home/mclaugr4/software/bin/taxit taxtable -t $REF.ids_only -d $TAXDB > 16S_bac.taxonomy
/home/mclaugr4/software/bin/taxit create \
  -P 16S_bac.refpkg \
  -l 16S_bac \
  -t $TREE \
  -s $STATS \
  -T 16S_bac.taxonomy \
  -i $REF.tax_map.csv \
  -f $REF.fasta \
  -p $COMPLETE.hmm \
  -S $COMPLETE.sto ###  \
###   -m 16S_bac.mask
# Reroot
/home/mclaugr4/software/bin/taxit reroot 16S_bac.refpkg

# Check the reference package
rppr check -c 16S_bac.refpkg

# Write the reference tree
rppr ref_tree -o 16S_bac-reftree.xml -c 16S_bac.refpkg

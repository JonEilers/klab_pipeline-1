#!/bin/bash

#$ -S /bin/bash
#$ -cwd
#$ -N mk.{title}
#$ -e makeref.err
#$ -o makeref.out

hmm_len() {{
    local result=$(grep "^LENG" $1 | awk '{{ print $2 }}')
    echo $result
}}


EVALUE=1e-5
PDCUTOFF=1e-2
TAXDB=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/make_reference_packages/ncbi_taxonomy.db
EUKTAXIDREX=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/make_reference_packages/update_euk_taxid_regex.txt
LEN_THRESHOLD=0.2

RECRUITED={title}.recruited
COMPLETE={title}.complete
AUTO1={title}.auto1
REF={title}.ref

SCRIPTS=/home/mclaugr4/bio/scripts/pplacer_pipeline_scripts/scripts

REMOVE_SHORT=$SCRIPTS/remove_short_seqs.py
TAXIDSOFFASTA=$SCRIPTS/taxids_of_fasta.py
MARKCONSENSUS=$SCRIPTS/mark_consensus.py
SM=/home/mclaugr4/software/bin/seqmagick

# Unalign, deduplicate taxa
$SM convert --deduplicate-taxa recruit.fasta $RECRUITED.fasta
$SM mogrify --dash-gap --ungap --first-name $RECRUITED.fasta

# Clean up names
$SM mogrify --pattern-replace '[\[\]\(\),;:"+]' '' $RECRUITED.fasta
$SM mogrify --pattern-replace "'" '' $RECRUITED.fasta

# A little hack find the minimum ungapped legnth relative to the 
# length of the HMM. We want to include sequences who's ungapped length is
# < $LEN_THRESHOLD*HMM_LENGTH
MIN_UNGAPPED_LEN=$(python -c "print int($(hmm_len {seed_hmm})*$LEN_THRESHOLD)")

$SM convert --min-ungapped-length $MIN_UNGAPPED_LEN $RECRUITED.fasta \
  $RECRUITED.tidy.fasta

# Generate an MSA from the sequences
muscle3.8.31_i86linux64 -quiet -in $RECRUITED.tidy.fasta -out $COMPLETE.fasta

# Trimming and Deduplication
# Trimal generates a mask (.pre.mask) relative to position in the alignment.
# Below, we update to be relative to consensus columns in the stockholm
# file for the final mask
trimal -automated1 -colnumbering -in $COMPLETE.fasta -out $AUTO1.pre_subset.afa > {title}.pre.mask
trimal -resoverlap 0.5 -seqoverlap 50 -in $AUTO1.pre_subset.afa \
  -out $AUTO1.afa
$SM convert --first-name --deduplicate-sequences --input-format fasta \
  $AUTO1.afa $AUTO1.dedup.fasta

 
# Pruning
FastTree -quiet $AUTO1.dedup.fasta > $AUTO1.fast.tre
rppr pdprune --never-prune-regex-from $EUKTAXIDREX --cutoff $PDCUTOFF \
  --names-only -o $AUTO1.to_exclude $AUTO1.fast.tre
seqmagick convert --exclude-from-file $AUTO1.to_exclude \
  $AUTO1.dedup.fasta $AUTO1.pruned.fasta

# ref fasta, sto, and hmm
$SM extract-ids $AUTO1.pruned.fasta -o $AUTO1.pruned.ids

######################################################################
# Build a new stockholm file, containing only pruned sequences, with a
# consensus consisting of the union of consensus columns and unmasked
# positions
$SM convert --include-from-file $AUTO1.pruned.ids \
  $COMPLETE.fasta $COMPLETE.pruned.fasta

# use mark_consensus.py to generate a $COMPLETE.sto which has the
# mask-included sites as consensus columns
$MARKCONSENSUS $COMPLETE.pruned.fasta {title}.pre.mask {title}.mask \
  --stockholm-out $COMPLETE.sto --masked-out $REF.fasta
rm -f {title}.pre.mask

hmmbuild --hand $COMPLETE.hmm $COMPLETE.sto

# make reference tree
case "{tree_method}" in 
  fasttree)
    FastTree -log $REF.stats -wag -gamma $REF.fasta > $REF.tre
    STATS=$REF.stats
    TREE=$REF.tre
    ;;
  raxml)
    fasta2phyml $REF.fasta
    raxmlHPC-PTHREADS-SSE3 -T 2 -m PROTGAMMAWAG -n {title} -s $REF.phymlAln
    STATS=RAxML_info.{title}
    TREE=RAxML_result.{title}
    ;;
  *)
    echo "Unknown tree: {tree_method}"
    exit 1
esac    

# make refpkg!
$TAXIDSOFFASTA $REF.fasta
/home/mclaugr4/software/bin/taxit taxtable -t $REF.ids_only -d $TAXDB > {title}.taxonomy
/home/mclaugr4/software/bin/taxit create \
  -P {title}.refpkg \
  -l {title} \
  -t $TREE \
  -s $STATS \
  -T {title}.taxonomy \
  -i $REF.tax_map.csv \
  -f $REF.fasta \
  -p $COMPLETE.hmm \
  -S $COMPLETE.sto \
  -m {title}.mask
# Reroot
/home/mclaugr4/software/bin/taxit reroot {title}.refpkg

# Check the reference package
rppr check -c {title}.refpkg

# Write the reference tree
rppr ref_tree -o {title}-reftree.xml -c {title}.refpkg

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
TAXDB=/home/rkodner/prep/kaboodle/data/taxonomy.db
EUKTAXIDREX=/home/rkodner/prep/noodle/data/euk_taxid_regex.txt
LEN_THRESHOLD=0.2

RECRUITED={title}.recruited
COMPLETE={title}.complete
AUTO1={title}.auto1
REF={title}.ref

SCRIPTS=/home/rkodner/prep/kaboodle/scripts/

REMOVE_SHORT=$SCRIPTS/remove_short_seqs.py
TAXIDSOFFASTA=$SCRIPTS/taxids_of_fasta.py
MARKCONSENSUS=$SCRIPTS/mark_consensus.py
SM=/home/rkodner/python2.7-sqlite3.7/bin/seqmagick

# first find sequences in the potential-reference sequence DB
hmmsearch --cpu 2 --noali --notextw -E $EVALUE -A $RECRUITED.sto \
  --domtblout $RECRUITED.domains.txt {seed_hmm} {ref_db} 

# test to make sure that we did recruit some sequences
if [ -s $RECRUITED.sto ]; then
  # make ref alignment

  # Get the lowest evalue sequence per domain
  $SCRIPTS/lowest_evalue_sequence.py $RECRUITED.sto $RECRUITED.domains.txt \
    $RECRUITED.trimmed.sto

  # Unalign, deduplicate taxa
  $SM convert --deduplicate-taxa $RECRUITED.trimmed.sto $RECRUITED.fasta
  $SM mogrify --dash-gap --ungap --first-name $RECRUITED.fasta

  # Clean up names
  $SM mogrify --pattern-replace '[\[\]\(\)l,;:"+]' '' $RECRUITED.fasta
  $SM mogrify --pattern-replace "'" '' $RECRUITED.fasta

  # A little hack find the minimum ungapped legnth relative to the 
  # length of the HMM. We want to include sequences who's ungapped length is
  # < $LEN_THRESHOLD*HMM_LENGTH
  MIN_UNGAPPED_LEN=$(python -c "print int($(hmm_len {seed_hmm})*$LEN_THRESHOLD)")

  $SM convert --min-ungapped-length $MIN_UNGAPPED_LEN $RECRUITED.fasta \
    $RECRUITED.tidy.fasta

  # Generate an MSA from the sequences
  muscle -quiet -in $RECRUITED.tidy.fasta -out $COMPLETE.fasta

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
  $SM convert --squeeze $AUTO1.pruned.fasta $REF.fasta
  #$SM convert $REF.fasta $REF.sto
  #hmmbuild $REF.hmm $REF.sto
  # Generate a list of remaining IDs
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
  fasta2phyml $REF.fasta
 # raxmlHPC-PTHREADS-SSE3 -T 2 -m PROTGAMMAWAG -n {title} -s $REF.phymlAln
   FastTree -log $REF.stats -wag -gamma $REF.phymlAln > $REF.tre

  # make refpkg!
  $TAXIDSOFFASTA $REF.fasta
  taxit taxtable -t $REF.ids_only -d $TAXDB > {title}.taxonomy
  taxit create \
    -P {title}.refpkg \
    -l {title} \
    -t {title}.ref.tre \
    -s {title}.ref.stats \
    -T {title}.taxonomy \
    -i $REF.tax_map.csv \
    -f $REF.fasta \
    -p $COMPLETE.hmm \
    -S $COMPLETE.sto \
    -m {title}.mask
  # Reroot
  taxit reroot {title}.refpkg

  # Check the reference package
  guppy check_refpkg -c {title}.refpkg

  # Write the reference tree
  rppr check -c {title}.refpkg
fi


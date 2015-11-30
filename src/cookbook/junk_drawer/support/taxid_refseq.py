import os

# set path as the CWD
path = os.path.dirname(os.path.realpath(__file__))

dl_path = path + '/dl/'

refseq_catalog = dl_path + 'RefSeq-release66.catalog'
catalog_dictionary = {}
with open(refseq_catalog, 'r') as file:
    lines = file.readlines()
    for line in lines:
        split_line = line.split('\t')
        taxid = split_line[0]
        gi = split_line[3]
        catalog_dictionary[gi] = taxid

refseq_full = dl_path + 'refseq_protein.66.archa_bacte_fungi_inver_mitoc_plant_plasm_plast_proto_viral.fa'
with open(refseq_full, 'r') as file1:
    lines = file1.readlines()
new_refseq_full = path + '/' + refseq_full.split('/')[-1].strip('fa') + 'tax.fasta'
with open(new_refseq_full, 'w') as output:
    for line in lines:
        if line.find('>') != -1:
            line = line.lstrip('>')
            split_line = line.split('|')
            gi = split_line[1]
            if gi in catalog_dictionary.keys():
                new_line = '>' + str(catalog_dictionary[gi]) + '|' + '|'.join(split_line)
                output.write(new_line)
                write_rest = True
                del catalog_dictionary[gi]
            else:
                print line, 'is not found in the catalog...'
                write_rest = False
        elif write_rest == True:
            output.write(line)

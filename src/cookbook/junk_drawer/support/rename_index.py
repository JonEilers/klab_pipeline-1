input = open('refseq_protein_66.MMETSP_071414.fasta', 'r')
input_list = input.readlines()
input.close()

counter = 0
output = open('refseq_protein_66.MMETSP_071414.reindexed.fasta', 'w')
for line in input_list:
    if line.find('>') != -1 and line.find('MMETSP') == -1:
        split_line = line.split('|')
        split_line[1] = '.'.join([split_line[1].split('.')[0],
                                  split_line[1].split('.')[1],
                                  str(counter)])
        counter += 1
        line = '|'.join(split_line)
    elif line.find('>') != -1 and line.find('MMETSP') != -1:
        split_line = line.split('|')
        split_line[1] = split_line[1] + '.' + str(counter)
        counter += 1
        line = '|'.join(split_line)
    output.write(line)
output.close()

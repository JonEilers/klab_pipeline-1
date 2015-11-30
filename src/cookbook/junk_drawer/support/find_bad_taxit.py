import sys

path = '/home/mclaugr4/bio/refpkg_project_071414/makerefs/'
merged = path + 'merged.dmp'
delnodes = path + 'delnodes.dmp'
tax_error = path + 'tax_errors.txt'

merged_dictionary = {}
with open(merged, 'r') as m:
    merged_dictionary = {int(x.split('\t|\t')[0]): int(x.split('\t|\t')[1].rstrip('\t|\n')) for x in m.readlines()}

with open(delnodes, 'r') as d:
    delnode_data = [int(x.split('\t|\n')[0]) for x in d.readlines()]

with open(tax_error, 'r') as t:
    replace_taxid_dictionary = {x.split('\t')[0]: x.split('\t')[1].strip('\n') for x in t.readlines()}

file = sys.argv[1]
input = open(file, 'r')
data = input.readlines()
input.close()
output = open(file, 'w')
keep = True
print file
for line in data:
    if line.find('>') != -1:
        keep = True
        split_line = line.split('|')
        split_line[0] = split_line[0].split('_')[0]
        if split_line[0] == '>' or split_line[0] == '>0':
            if replace_taxid_dictionary.keys().count(split_line[-1].strip('\n')) != 0:
                split_line[0] = '>' + str(replace_taxid_dictionary[split_line[-1].strip('\n')])
                print split_line[-1].strip('\n'), 'now has taxid', replace_taxid_dictionary[
                    split_line[-1].strip('\n')], '...'
            else:
                print '###############Error###############'
                print split_line[-1].strip('\n'), 'needs to be added to the error file...'
        elif split_line[0].lstrip('>') != '':
            print line
            tax_id = int(split_line[0].lstrip('>'))
            if merged_dictionary.keys().count(tax_id) != 0:
                print file, tax_id, merged_dictionary[tax_id], 'found in merged...'
                split_line[0] = '>' + str(merged_dictionary[tax_id])
            if delnode_data.count(tax_id) != 0:
                print file, tax_id, 'found in delnodes...'
                keep = False
        if keep == True:
            line = '|'.join(split_line)
            output.write(line)
    if line.find('>') == -1 and keep == True:
        output.write(line)

output.close()

import os
import itertools

path = './'

file_list = os.listdir(path)

for file in file_list:
    if file.find('_change.tsv') != -1:
        input = open(path + file, 'r')
        data_dictionary = {}
        for line in input:
            split_line = line.strip('\n').split('\t')
            gene = split_line[0]
            if gene == 'gene':
                col_list = split_line
            else:
                for delta in split_line:
                    site = col_list[split_line.index(delta)]
                    if split_line.index(delta) != 0:
                        if site in data_dictionary.keys():
                            data_dictionary[site].append((gene, float(delta)))
                        else:
                            data_dictionary[site] = [(gene, float(delta))]
        output = open(path + file.split('.')[0] + '_T10.tsv', 'w')
        for site, data_tuple in data_dictionary.iteritems():
            data_tuple.sort(key=lambda tup: tup[1])
            output.write(
                '\n'.join('\t'.join([l[0], site, str(l[1])]) for l in data_tuple[0:10] + data_tuple[-11:-1]) + '\n')
        output.close()

color_dictionary = {'C_U_1_8': 'chr1', 'C_U_8_3': 'chr1', 'C_U_3_20': 'chr1', 'U_S_1_8': 'chr12', 'U_S_8_3': 'chr12',
                    'U_S_3_20': 'chr12', 'S_D_1_8': 'chr19', 'S_D_8_3': 'chr19', 'S_D_3_20': 'chr19'}
cyto_list = ['gpos100', 'gpos75', 'gpos66', 'gpos50', 'gpos33', 'gpos25', 'gvar', 'gneg', 'acen', 'stalk']
lib_change_key = {'EC_U_1_8': 'EU_S_1_8', 'EU_S_1_8': 'ES_D_1_8', 'EC_U_8_3': 'EU_S_8_3', 'EU_S_8_3': 'ES_D_8_3',
                  'EC_U_3_20': 'EU_S_3_20', 'EU_S_3_20': 'ES_D_3_20'}
site_order = ['EC_U_1_8', 'EU_S_1_8', 'ES_D_1_8', 'EC_U_8_3', 'EU_S_8_3', 'ES_D_8_3', 'EC_U_3_20', 'EU_S_3_20',
              'ES_D_3_20']
for each in file_list:
    if each.find('_T10.tsv') != -1 and each[0] == 'E':
        file = path + each
        input = open(file, 'r')
        taxa_count = {}
        for line in input:
            neg = False
            split_line = line.strip('\n').split('\t')
            gene = split_line[0]
            site = split_line[1]
            delta = int(float(split_line[2]))
            if str(delta).find('-') != -1:
                neg = True
            # making circos file
            chr = 'band'
            parent = each[0] + site
            ID = site
            LABEL = site
            START = '0'
            COLOR = color_dictionary[LABEL]
            total = ('chr', '-', parent, LABEL, COLOR)
            key = (chr, parent, gene, COLOR, neg)
            taxa_count[key] = abs(delta)
            if total in taxa_count.keys():
                taxa_count[total] = taxa_count[total] + abs(delta)
            else:
                taxa_count[total] = abs(delta)
        input.close()
        chr_list = []
        band_list = []
        parent_dictionary = {}
        for tuple, count in taxa_count.iteritems():
            if tuple[0] == 'chr':
                chr_list.append((tuple, count))
                chr_list.sort(key=lambda l: site_order.index(l[0][2]))
                parent_dictionary[tuple[2]] = count
            elif tuple[0] == 'band':
                band_list.append((tuple, count))
                band_list.sort(key=lambda l: site_order.index(l[0][1]))
        output = open('karyotype.' + file.split('/')[1].split('.')[0] + '.txt', 'w')
        bands_text = open('bands.' + file.split('/')[1].split('.')[0] + '.txt', 'w')
        for (tuple, count) in chr_list:
            output.write(' '.join([tuple[0], tuple[1], tuple[2], tuple[3], '0', str(count), tuple[4]]) + '\n')
        # cyto_index = 0
        func_dictionary = {}
        for (tuple, count) in band_list:
            if tuple[4] == True:
                cyto_index = 7
                COLOR = 'blue'
            else:
                cyto_index = 0
                COLOR = 'red'
            start = parent_dictionary[tuple[1]] - count
            stop = parent_dictionary[tuple[1]]
            output.write(
                ' '.join([tuple[0], tuple[1], tuple[2], tuple[2], str(start), str(stop), cyto_list[cyto_index]]) + '\n')
            bands_text.write(' '.join([tuple[1], str(start), str(stop), tuple[2]]) + '\n')
            if tuple[2] in func_dictionary.keys():
                func_dictionary[tuple[2]].append((tuple[1], str(start), str(stop), COLOR))
            else:
                func_dictionary[tuple[2]] = [(tuple[1], str(start), str(stop), COLOR)]
            parent_dictionary[tuple[1]] = start
        output.close()
        bands_text.close()
        link_lib = open('link.' + file.split('/')[1].split('.')[0] + '.txt', 'w')
        for func, start_stop_list in func_dictionary.iteritems():
            nr_set = list(itertools.product(start_stop_list, start_stop_list))
            for link_tup in nr_set:
                if link_tup[0] != link_tup[1] and link_tup[0][0] in lib_change_key.keys():
                    if lib_change_key[link_tup[0][0]] == link_tup[1][0]:
                        link_lib.write(
                            ' '.join(link_tup[0][:3]) + ' ' + ' '.join(link_tup[1][:3]) + ' color=' + link_tup[0][
                                -1] + '\n')

        link_lib.close()

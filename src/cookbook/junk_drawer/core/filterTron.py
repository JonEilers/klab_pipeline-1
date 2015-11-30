Mpath = '/home/mclaugr4/bio/scripts_built/MBARI/'
data_in = Mpath + 'data_in/'
path = '/home/mclaugr4/bio/scripts_built/lineage/taxonomy-upa/data/'
work = Mpath + 'work/'
domain = path + 'domain/'

file = data_in + 'Eukaryotic_taxa_look_up_table_for binning.txt'
input = open(file, 'rU')
euk_bin_dictionary = {}
for line in input:
    split_line = line.strip('\n').strip('\r').split('\t')
    taxon = split_line[0]
    high_taxon = split_line[1]
    sub_high_taxon = split_line[2]
    metabo = split_line[3]
    euk_bin_dictionary[taxon] = high_taxon, sub_high_taxon, metabo
input.close()

file = data_in + 'MBARI_metagenome_normalization_factors.txt'
# file = work + 'norm_factors.tsv'
input = open(file, 'rU')
norm_factors = {}
for line in input:
    split_line = line.strip('\n').strip('\r').split('\t')
    site = split_line[0]
    if site != 'name':
        size = split_line[1]
        read_count = split_line[4]
        normalization = split_line[5]
        norm_factors[site + size] = read_count, normalization

input.close()

file = data_in + 'whog.txt'
# output = open(data_in + 'cog_func.tsv','w')
input = open(file, 'ru')
COG_func = {}
for line in input:
    if line.find('[') != -1 and line.find('COG') != -1:
        split_line = line.strip('\n').strip('\r').split(']')
        func_cat = split_line[0].replace('[', '')
        COG_id = split_line[1].split(' ')[1]
        func = ' '.join(split_line[1].split(' ')[2:-1])
        COG_func[COG_id] = func_cat, func
        # output.write('\t'.join([COG_id,func_cat,func]) + '\n')
# output.close()
input.close()

# file = work + 'MBARI_anno_best_conf_COUNTED.tsv'
# file = work + 'Confident_scores_COUNTED.tsv'
file = work + 'annotated_final_COUNTED.tsv'
input = open(file, 'rU')
out0 = 'Archaea'
out1 = 'Bacteria'
out2 = 'Eukaryota'
out3 = 'Viruses'

output0 = open(domain + out0 + '_anno.tsv', 'w')
output1 = open(domain + out1 + '_anno.tsv', 'w')
output2 = open(domain + out2 + '_anno.tsv', 'w')
output3 = open(domain + out3 + '_anno.tsv', 'w')

# output0 = open(domain + out0 + '_unknown.tsv','w')
# output1 = open(domain + out1 + '_unknown.tsv','w')
# output2 = open(domain + out2 + '_unknown.tsv','w')
# output3 = open(domain + out3 + '_unknown.tsv','w')

out_dictionary = {out0: output0, out1: output1, out2: output2, out3: output3}

for line in input:
    line = line.strip('\n').strip('\r')
    split_line = line.split('\t')
    if split_line[0] == 'gene':
        columns = [split_line[0], split_line[1], split_line[2], split_line[5], 'normalized_taxa_count', split_line[3],
                   split_line[4], 'high_level_classification', 'sub_high_level_classification', 'metabolism',
                   'read_count_library', 'Normalization_factor', 'functional_category', 'functional_description']
        output0.write('\t'.join(columns) + '\n')
        output1.write('\t'.join(columns) + '\n')
        output2.write('\t'.join(columns) + '\n')
        output3.write('\t'.join(columns) + '\n')
    if split_line[0] != 'gene':
        gene = split_line[0]
        site = split_line[1]
        if site == 'costal':
            site = 'coastal'
        size = split_line[2]
        if size == '20-Mar':
            size = '3-20'
        scientific_name = split_line[3].replace(' ', '_')
        domain_name = split_line[4]
        taxa_count = split_line[5]
        if euk_bin_dictionary.has_key(scientific_name) == True:
            high_taxa = euk_bin_dictionary[scientific_name][0]
            sub_high_taxa = euk_bin_dictionary[scientific_name][1]
            metabo = euk_bin_dictionary[scientific_name][2]
        else:
            high_taxa = 'not_found'
            sub_high_taxa = 'not_found'
            metabo = 'not_found'
        read_count = norm_factors[site + size][0]
        norm_factor = norm_factors[site + size][1]
        norm_tcount = str(float(norm_factor) * float(taxa_count))
        if gene in COG_func.keys():
            func_cat = COG_func[gene][0]
            func = COG_func[gene][1]
        else:
            func_cat = ''
            func = ''
        if out_dictionary.has_key(domain_name) == True:
            out_dictionary[domain_name].write('\t'.join(
                [gene, site, size, taxa_count, norm_tcount, scientific_name, domain_name, high_taxa, sub_high_taxa,
                 metabo, read_count, norm_factor, func_cat, func]) + '\n')
input.close()
output0.close()
output1.close()
output2.close()
output3.close()

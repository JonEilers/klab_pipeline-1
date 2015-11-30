import os
import sys
import shutil
import subprocess

path = os.path.dirname(os.path.realpath(__file__))
directory = sys.argv[1]
# package_path = path + '/' + directory
package_path = directory
stat_file = sys.argv[2]
with open(stat_file, 'w') as i:
    i.write('gene\ttotal\tBacteria\tEukaryota\tArchaea\tseq_len\tnum_seqs\n')
    for root, dirs, files in os.walk(package_path):
        gene = root.split('/')[-1].split('.')[0]
        if files != [] and gene != '':
            if len(files) < 10 and root.find('.refpkg') != -1:
                print root
                print len(files)
                shutil.rmtree(root)
            else:
                write_list = [gene]
                tax_map_file = [x for x in files if x.find('tax_map') != -1][0]
                with open(root + '/' + tax_map_file, 'r') as r:
                    lines = r.readlines()
                    tax_map = [str(x.split(',')[0]) for x in lines[1:]]
                tax_map = list(set(tax_map))
                taxonomy_file = [x for x in files if x.find('taxonomy') != -1][0]
                with open(root + '/' + taxonomy_file, 'r') as o:
                    lines = o.readlines()
                    count_dict = {'total': len(tax_map), 'Bacteria': 0, 'Eukaryota': 0, 'Archaea': 0}
                    taxid2Domain = {'2': 'Bacteria', '2759': 'Eukaryota', '2157': 'Archaea'}
                    for line in lines:
                        split_line = [x.replace('\"', '') for x in line.split(',')]
                        tax_id = split_line[0]
                        if tax_id in tax_map:
                            for domain in taxid2Domain.keys():
                                if split_line.count(domain) != 0:
                                    # if domain == '2759' and gene == 'SSU_16S_bac':
                                    #	print filter(None, split_line)
                                    count_dict[taxid2Domain[domain]] = count_dict[taxid2Domain[domain]] + 1
                write_list.extend([str(count_dict['total']), str(count_dict['Bacteria']),
                                   str(count_dict['Eukaryota']), str(count_dict['Archaea'])])
                fasta_file = [x for x in files if x.find('fasta') != -1][0]
                out = subprocess.Popen(['seqmagick', 'info', root + '/' + fasta_file],
                                       stdout=subprocess.PIPE).communicate()[0]
                header = out.split('\n')[0].split('\t')
                info = out.split('\n')[1].split('\t')
                write_list.extend([str(info[header.index('avg_len')]), str(info[header.index('num_seqs')])])
                i.write('\t'.join(write_list) + '\n')

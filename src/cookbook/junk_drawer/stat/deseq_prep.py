import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Built to use the standard output of countbot
file = sys.argv[1]
group_name = sys.argv[2]
out_file = sys.argv[3]
data = pd.DataFrame.from_csv(file, sep='\t', header=0, index_col=False)
print data.head()
#  metagenome list

sra_order = ['SRR304684', 'SRR064444', 'SRR304656', 'SRR064446', 'SRR064448',
             'SRR064450', 'SRR304668', 'SRR304683', 'SRR304671', 'SRR304672', 'SRR070081',
             'SRR304673', 'SRR070082', 'SRR304674', 'SRR070083', 'SRR304680', 'SRR070084'
             ]
'''
#  transcriptome list
sra_order = ['SRR064445', 'SRR064447', 'SRR064449', 'SRR064451']
'''
exclude_list = ['null_domain', 'root', 'metagenomes', 'environmental sample', 'fuzzy_archaea', 'fuzzy_viruses',
                'fuzzy_null', 'fuzzy_unknown', 'fuzzy_bacteria', 'cellular_organisms', 'metagenomes', 'fuzzy_eukaryota',
                'fuzzy_root', 'fuzzy_cellular_organisms', 'unclassified sequences', 'cellular organisms', 'Viruses']


data = data[data['sra_id'].isin(sra_order)]
data = data[~data['domain_name'].isin(exclude_list)]

print data.head()
data_summed = pd.DataFrame(data.groupby([group_name, 'sra_id']).sum()).reset_index()
print data_summed.head()

# for just including the groups that are present in all samples
# d = data_summed.pivot(index=group_name, columns='sra_id', values='taxa_count').dropna()
# for including all and adding empty values for missing groups in samples
d = data_summed.pivot(index=group_name, columns='sra_id', values='count'
                      ).fillna(0)
d.to_csv(group_name + '.' + out_file)
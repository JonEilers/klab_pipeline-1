import os
import sys
import pandas as pd

count_file = sys.argv[1]
meta_file = sys.argv[2]
padj_file_list = sys.argv[3].split(',')
outfile = sys.argv[4]

data = pd.DataFrame.from_csv(count_file, sep='\t', header=0, index_col=False)
meta_data = pd.DataFrame.from_csv(meta_file, sep=',', header=0, index_col=False)

zones = list(set(meta_data.zone))
colors = ['#0000ff', '#00ff00']

sra_order = ['SRR304684', 'SRR064444', 'SRR304656', 'SRR064446', 'SRR064448',
             'SRR064450', 'SRR304668', 'SRR304683', 'SRR304671', 'SRR304672', 'SRR070081',
             'SRR304673', 'SRR070082', 'SRR304674', 'SRR070083', 'SRR304680', 'SRR070084'
             ]

data = data[data['sra_id'].isin(sra_order)]
data = data[~data['gene'].str.contains('SSU')]

#  Make oxic and suboxic padj gene lists
oxic_list = []
suboxic_list = []
for padj_file in padj_file_list:  # todo: separate out oxic and suboxic genes
    padj_df = pd.DataFrame.from_csv(padj_file, sep=',', header=0, index_col=False)
    column_nm = padj_df.columns.tolist()
    column_nm[0] = 'gene'
    padj_df.columns = column_nm
    padj_df = padj_df[(padj_df['padj'] < 0.05)]
    oxic_padj_df = padj_df[(padj_df['log2FoldChange'] < 0)]
    suboxic_padj_df = padj_df[(padj_df['log2FoldChange'] > 0)]
    oxic_list.extend(list(set(oxic_padj_df['gene'])))
    suboxic_list.extend(list(set(suboxic_padj_df['gene'])))
oxic_list = list(set(oxic_list))
suboxic_list = list(set(suboxic_list))
gene_dict = {'oxic':oxic_list, 'suboxic':suboxic_list}

for zone in zones:
    gene_list = gene_dict[zone]
    zone_ids = list(meta_data.loc[(meta_data.zone == zone)].sra_id)
    count_data = data[data['gene'].isin(gene_list)]
    zone_data = count_data[count_data['sra_id'].isin(zone_ids)][['gene','count']].groupby(['gene']).sum()
    zone_data['count'] = zone_data['count']/100
    zone_data['count'] = 'W' + zone_data['count'].astype(str)
    color = colors[zones.index(zone)]
    zone_data['color_code'] = color
    zone_data.to_csv(zone + '_' + outfile, sep=' ', header=False)

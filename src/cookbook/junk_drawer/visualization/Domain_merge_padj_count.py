import sys

import pandas as pd

count_file = sys.argv[1]
padj_file_list = sys.argv[2].split(',')
outfile = sys.argv[3]

count_df = pd.DataFrame.from_csv(count_file, sep='\t', header=0, index_col=False)
gene_list = []
for padj_file in padj_file_list:
    padj_df = pd.DataFrame.from_csv(padj_file, sep=',', header=0, index_col=False)
    gene_list.extend(list(set(padj_df['gene'])))
gene_list = list(set(gene_list))

count_df = count_df[count_df['gene'].isin(gene_list)]
count_df.to_csv(outfile)

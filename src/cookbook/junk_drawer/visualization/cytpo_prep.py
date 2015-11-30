import sys

import pandas as pd


#  magic numbers
source = 'sra_id'
target = 'cluster'

data_file = sys.argv[1]
data_df = pd.DataFrame.from_csv(data_file, sep='\t', header=0, index_col=False)

print data_df.head()

cyto_list = []
colnames = list(data_df.columns.values)
for val in data_df.values:
    source_val = val[colnames.index(source)]
    target_val = val[colnames.index(target)]
    cyto_list.append([source_val, 'contains', target_val])
# cyto_df = pd.DataFrame(cyto_list)
# cyto_df.to_csv('_'.join([source, target, 'cyto_prep.sif']), sep='\t')
out_file = '_'.join([source, target, 'cyto_prep.sif'])
with open(out_file, 'w') as o:
    o.write('\n'.join(['\t'.join(x) for x in cyto_list]))

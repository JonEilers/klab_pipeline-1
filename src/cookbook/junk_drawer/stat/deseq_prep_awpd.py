import sys
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Built to use the standard output of countbot
file = sys.argv[1]
group_name = sys.argv[2]
out_file = sys.argv[3]
data = pd.DataFrame.from_csv(file, sep=',', header=0, index_col=False)
sra_order = ['SRR304684','SRR064444','SRR304656','SRR064446','SRR064448','SRR064450','SRR304668',
	'SRR304683','SRR304671','SRR304672','SRR070081','SRR304673','SRR070082','SRR304674','SRR070083',
	'SRR304680','SRR070084']
data = data[data['sra_id'].isin(sra_order)]
print data.head()
data_mean = pd.DataFrame(data.groupby([group_name,'sra_id']).mean())['awpd'].reset_index()
print data_mean.head()
data_mean['awpd'] = np.round(data_mean['awpd'] * 1000, 0)
print data_mean.head()
d = data_mean.pivot(index=group_name, columns='sra_id', values='awpd').fillna(0)

d.to_csv(group_name + '.awpd.' +  out_file)
import sys

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file = sys.argv[1]
meta = sys.argv[2]
outfile = sys.argv[3]

data = pd.DataFrame.from_csv(file, sep=',', header=0, index_col=False)
meta_data = pd.DataFrame.from_csv(meta, sep=',', header=0, index_col=False)
meta_data['zone'] = meta_data['zone'].str.replace('\n', '')

# libraries to use
sra_order = ['SRR304684', 'SRR064444', 'SRR304656', 'SRR064446', 'SRR064448',
             'SRR064450', 'SRR304668', 'SRR304683', 'SRR304671', 'SRR304672', 'SRR070081',
             'SRR304673', 'SRR070082', 'SRR304674', 'SRR070083', 'SRR304680', 'SRR070084',
             'SRR064445', 'SRR064447', 'SRR064449', 'SRR064451'
             ]

exclude_list = ['null_domain', 'root', 'metagenomes', 'environmental sample', 'fuzzy_archaea', 'fuzzy_viruses',
                'fuzzy_null', 'fuzzy_unknown', 'fuzzy_bacteria', 'cellular_organisms', 'metagenomes', 'fuzzy_eukaryota',
                'fuzzy_root', 'fuzzy_cellular_organisms']

years = list(set(meta_data.year))
zones = list(set(meta_data.zone))
aas = list(set(meta_data.seq_type))

color_list = ['r', 'y', 'b']
marker_list = ['s', 'o']

data = data[data['sra_id'].isin(sra_order)]
data = data[data['awpd'] > 0]
# Switch the "~" to nothing to only include SSUs
data = data[~data['gene'].str.contains('SSU')]
data_mean = pd.DataFrame(data.groupby(['domain_name', 'sra_id']).mean()).reset_index()

for domain in set(data_mean.domain_name):
    if exclude_list.count(domain) == 0:
        print domain
        domain_data = data_mean.loc[(data_mean.domain_name == domain)]
        fig, ax = plt.subplots()
        legend_list = []
        for year in years:
            if str(year) == '2008':
                year_ids = list(meta_data.loc[(meta_data.year == year)].sra_id)
                year_data = domain_data[domain_data['sra_id'].isin(year_ids)]
                for aa in aas:
                    aa_ids = list(meta_data.loc[(meta_data.seq_type == aa)].sra_id)
                    aa_data = year_data[year_data['sra_id'].isin(aa_ids)]
                    y = [int(meta_data.loc[meta_data.sra_id == n]['depth']) for n in
                         aa_data.sra_id
                         ]
                    x = aa_data.awpd

                    colors = [color_list[aas.index(aa)] for i in range(0, len(aa_data))]
                    sizes = [int(int(meta_data.loc[(meta_data.sra_id == a)].lib_size) / 10000) for a in aa_data.sra_id]
                    markers = [marker_list[zones.index(meta_data.zone.where(meta_data.sra_id == a, np.nan).max())] for a
                               in
                               aa_data.sra_id]
                    for _x, _y, _c, _m, _s in zip(x, y, colors, markers, sizes):
                        ax.scatter(_x, _y, c=_c, s=_s, marker=_m)
                    lo = ax.scatter([], [], c=colors, s=100)
                    legend_list.append(lo)

        y = [int(meta_data.loc[meta_data.sra_id == n]['depth']) for n in
             domain_data.sra_id
             ]
        x = domain_data.awpd
        z = np.polyfit(x, y, 1)
        p = np.poly1d(z)
        # plt.plot(x, p(x), 'k-')
        t = str('y = %.6fx + s(%.6f)' % (z[0], z[1]))
        equ = ax.legend([], [], loc='lower center',
                        title=t, scatterpoints=1, fontsize=12
                        )
        l1 = plt.scatter([], [], s=100, c='black', marker='s')
        l2 = plt.scatter([], [], s=100, c='black', marker='o')

        labels = ["10", "50", "100", "200"]

        leg = ax.legend([l1, l2], zones, loc='center left', title='Zone',
                        scatterpoints=1, fontsize=12)
        ax.legend(legend_list, aas, scatterpoints=1, loc='center right', title='Year', fontsize=12)
        plt.gca().add_artist(leg)
        # plt.gca().add_artist(equ)
        plt.gca().invert_yaxis()
        # plt.xlim([0,2])
        plt.ylim([850, -100])
        for label in (ax.get_xticklabels() + ax.get_yticklabels()):
            label.set_fontsize(16)
        plt.ylabel('depth(m)', fontsize=16)
        plt.xlabel('AWPD', fontsize=16)
        plt.title(domain + ' AWPD by depth and seq type for COGs in 2008 ETSP OMZ')
        plt.savefig(domain + '.' + outfile)
        plt.clf()

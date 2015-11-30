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

# metagenome list

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
                'fuzzy_root', 'fuzzy_cellular_organisms', 'Viruses']

years = list(set(meta_data.year))
zones = list(set(meta_data.zone))

color_list = ['y', 'r', 'b']
marker_list = ['r', 'b']

data = data[data['sra_id'].isin(sra_order)]
# Switch the "~" to nothing to only include SSUs
data = data[~data['gene'].str.contains('SSU')]
data_mean = data  # pd.DataFrame(data.groupby(['sra_id']).mean()).reset_index()

fig, ax = plt.subplots()
legend_list = []
for year in years:
    fig, ax = plt.subplots()
    year_ids = list(meta_data.loc[(meta_data.year == year)].sra_id)
    year_data = data_mean[data_mean['sra_id'].isin(year_ids)]
    year_data = year_data[~year_data['domain_name'].isin(exclude_list)]
    print year_data.head()
    # y = [int(meta_data.loc[meta_data.sra_id == n]['depth']) for n in
    #     year_data.sra_id
    #     ]
    x = year_data.awpd
    y = year_data.quadratic
    colors = [color_list[years.index(year)] for i in range(0, len(year_data))]
    # colors = [marker_list[zones.index(meta_data.zone.where(meta_data.sra_id == a, np.nan).max())] for a in
    #           year_data.sra_id]
    # sizes = [int(int(meta_data.loc[(meta_data.sra_id == a)].lib_size) / 10000) for a in year_data.sra_id]
    # markers = [marker_list[zones.index(meta_data.zone.where(meta_data.sra_id == a, np.nan).max())] for a in
    #           year_data.sra_id]
    # for _x, _y, _c, _m, _s in zip(x, y, colors, markers, sizes):
    #    ax.scatter(_x, _y, c=_c, s=_s, marker=_m, alpha=0.5)
    for _x, _y, _c, in zip(x, y, colors):
        ax.scatter(_x, _y, c=_c, alpha=0.25)


    # add line to all series
    # z = zip(x,y)
    # z.sort(key=lambda x:x[1])
    # x,y = zip(*z)
    # ax.plot(x, y, color_list[years.index(year)])
    #

    lo = ax.scatter([], [], c=colors, s=100)
    legend_list.append(lo)

    y = [int(meta_data.loc[meta_data.sra_id == n]['depth']) for n in
         data_mean.sra_id
         ]
    x = data_mean.awpd
    z = np.polyfit(x, y, 1)
    p = np.poly1d(z)
    # plt.plot(x, p(x), 'k-')
    t = str('y = %.6fx + s(%.6f)' % (z[0], z[1]))
    equ = ax.legend([], [], loc='lower center',
                    title=t, scatterpoints=1, fontsize=12)

    l1 = plt.scatter([], [], s=100, c='black', marker='s')
    l2 = plt.scatter([], [], s=100, c='black', marker='o')

    labels = ["10", "50", "100", "200"]

    leg = leg = ax.legend([l1, l2], zones, loc='center left', title='Zone',
                          scatterpoints=1, fontsize=12)

    ax.legend(legend_list, years, scatterpoints=1, loc='lower right', title='Year', fontsize=12)
    plt.gca().add_artist(leg)
    # plt.gca().add_artist(equ)
    # plt.gca().invert_yaxis()
    # plt.ylim([850, -100])
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)
    plt.ylabel('depth(m)', fontsize=16)
    plt.xlabel('AWPD', fontsize=16)
    plt.title('AWPD by depth and year for COGs in ETSP OMZ')
    plt.savefig(str(year) + '_' + outfile)
    plt.clf()

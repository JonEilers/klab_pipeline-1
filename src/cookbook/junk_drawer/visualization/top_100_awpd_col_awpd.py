import sys
import math

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

file = sys.argv[1]
awpd_file = sys.argv[2]
awpd_data = pd.DataFrame.from_csv(awpd_file, sep=',', header=0, index_col=False)[
    ['cluster', 'sra_id', 'domain_name', 'awpd']]
data = pd.DataFrame.from_csv(file, sep='\t', header=0, index_col=False)
data = pd.merge(data, awpd_data, how='left', on=['cluster', 'sra_id', 'domain_name'])
sra2name = {'SRR304684': '2008_15m', 'SRR064444': '2008_50m', 'SRR304656': '2008_65m', 'SRR064446': '2008_85m',
            'SRR064448': '2008_110m', 'SRR064450': '2008_200m', 'SRR304668': '2008_500m', 'SRR304683': '2008_800m',
            'SRR304671': '2009_35m', 'SRR304672': '2009_50m', 'SRR070081': '2009_70m', 'SRR304673': '2009_110m',
            'SRR070082': '2009_200m', 'SRR304674': '2010_50m', 'SRR070083': '2010_80m', 'SRR304680': '2010_110m',
            'SRR070084': '2010_150m'}
sra_order = ['SRR304684', 'SRR064444', 'SRR304656', 'SRR064446', 'SRR064448', 'SRR064450', 'SRR304668',
             'SRR304683', 'SRR304671', 'SRR304672', 'SRR070081', 'SRR304673', 'SRR070082', 'SRR304674', 'SRR070083',
             'SRR304680', 'SRR070084']
for domain_name in set(data.domain_name):
    domain_data = data.loc[(data.domain_name == domain_name)]
    domain_data = domain_data[domain_data['sra_id'].isin(sra2name.keys())]

    # Heatmaps
    heatmap_data = pd.DataFrame(columns=set(domain_data.sra_id))
    for sra_id in set(domain_data.sra_id):
        sra_data = domain_data.loc[(domain_data.sra_id == sra_id)].sort(['awpd'], ascending=[False]
                                                                        ).reset_index()[
                       ['cluster', 'sra_id', 'domain_name', 'count', 'awpd']
                   ][:100]
        heatmap_data[sra_data.sra_id[0]] = sra_data.awpd
    heatmap_data.to_csv(domain_name + '_100_awpd.awpd_col.csv')
    heatmap_data.fillna(0, inplace=True)
    try:
        heatmap_data = heatmap_data[sra_order]
    except:
        print domain_name
    # Plot it out
    fig, ax = plt.subplots()
    heatmap = ax.pcolor(heatmap_data)  # , cmap=plt.cm.jet)

    # legend
    cbar = plt.colorbar(heatmap)
    cbar.ax.get_yaxis().set_ticks([])
    heat_range = range(0, int(math.ceil(heatmap_data.max().max())))
    for j in heat_range:
        cbar.ax.text(1.5, float(1 + j) / float(len(heat_range)), '$' + str(1 + j) + '$', ha='center', va='center')
    cbar.ax.get_yaxis().labelpad = 45
    cbar.ax.set_ylabel('AWPD', rotation=270)

    # Format
    fig = plt.gcf()
    fig.set_size_inches(12, 12)

    # turn off the frame
    ax.set_frame_on(True)

    # put the major ticks at the middle of each cell
    ax.set_yticks(np.arange(heatmap_data.shape[0]), minor=False)
    ax.set_xticks(np.arange(heatmap_data.shape[1]), minor=False)


    # want a more natural, table-like display
    ax.invert_yaxis()
    ax.xaxis.tick_top()

    # Set the labels

    # label
    xlabels = [sra2name[x] for x in sra_order]
    ylabels = list(xrange(101))[1:]
    ax.set_xticklabels(xlabels, minor=False, ha='left')
    ax.set_yticklabels(ylabels, minor=False, va='top')
    ax.axes.get_yaxis().set_visible(True)


    # rotate the
    plt.xticks(rotation=25)

    ax.grid(b=True, which='major', color='w', linestyle='-')

    # Turn off all the ticks
    ax = plt.gca()

    for t in ax.xaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    for t in ax.yaxis.get_major_ticks():
        t.tick1On = False
        t.tick2On = False
    plt.draw()
    fig.savefig(domain_name + '_100_awpd.awpd_col.jpeg')
    plt.clf()

#!/usr/bin/env python

import matplotlib

matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

from matplotlib import pyplot as plt
import pandas as pd

from klab.process.file_manager import read_df_from_file, write_df_to_file

from lib.stacked_bar_graph import StackedBarGrapher


def massage_data(df):
    # group, reshape and replace missing values
    b = pd.DataFrame(df.groupby(['domain_name_12', 'domain_name_14']).size())
    c = b.unstack()
    c.fillna(0, inplace=True)  # replace NaN

    # clean up column names
    c.reset_index(inplace=True)
    c.columns = c.columns.get_level_values(1)
    c.rename(columns={'AAsame': 'Same', 'top level': 'Top Level', 'zNone': 'New Placements'}, inplace=True)

    # clean up row names
    c[''][c[''] == 'zNone'] = 'New Placements'
    c[''][c[''] == 'top level'] = 'Top Level'

    return c


def plot_data(file_name, type):
    c = read_df_from_file(file_name)
    c.set_index(['Unnamed: 0'], inplace=True)  # set index to first column
    c = c.div(c.sum(axis=1), axis=0)  # normalize the data

    sbg = StackedBarGrapher()

    d = c.as_matrix()

    d_labels = list(c.index.values)

    # ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
    d_colors = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale

    fig = plt.figure()

    ax = fig.add_subplot(111)
    sbg.stackedBarPlot(ax,
                       d,
                       d_colors,
                       xLabels=d_labels,
                       gap=0.05,
                       endGaps=True,
                       scale=True
                       )
    plt.title(type + ' Placements 2012 to 2014')

    fig.subplots_adjust(bottom=0.4)
    plt.tight_layout()
    plt.savefig('/shared_projects/MBARI/' + type.lower() + '_placement_bar.pdf')
    plt.close(fig)
    del fig


if __name__ == '__main__':
    df = read_df_from_file('/data/MBARI_merged.tsv', low_memory=False)

    # rename for nicer ordering of graphs
    df['domain_name_14'][df['domain_name_12'] == df['domain_name_14']] = 'AAsame'
    df['domain_name_12'][df.domain_name_12 == 'None'] = 'zNone'
    df['domain_name_14'][df.domain_name_14 == 'None'] = 'zNone'

    t = 'All'
    d2 = massage_data(df)
    file_name = '/shared_projects/MBARI/' + t.lower() + '_placements.csv'
    write_df_to_file(d2, file_name)
    plot_data(file_name, t)

    t = 'Fuzzy'
    a = df[df['placement_type_12'] == t.lower()]
    d2 = massage_data(a)
    file_name = '/shared_projects/MBARI/' + t.lower() + '_placements.csv'
    write_df_to_file(d2, file_name)
    plot_data(file_name, t)

    t = 'Confident'
    a = df[df['placement_type_12'] == t.lower()]
    d2 = massage_data(a)
    file_name = '/shared_projects/MBARI/' + t.lower() + '_placements.csv'
    write_df_to_file(d2, file_name)
    plot_data(file_name, t)

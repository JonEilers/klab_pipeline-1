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


def plot_data(data_file, plot_file, title, colors, scale_chart=False):
    c = read_df_from_file(data_file)
    c.set_index(['Unnamed: 0'], inplace=True)  # set index to first column
    if scale_chart:
        c = c.div(c.sum(axis=1), axis=0)  # normalize the data because sbg ain't so good at that

    sbg = StackedBarGrapher()

    d = c.as_matrix()

    d_labels = list(c.index.values)

    fig = plt.figure()

    ax = fig.add_subplot(111)
    sbg.stackedBarPlot(ax,
                       d,
                       colors,
                       xLabels=d_labels,
                       gap=0.05,
                       endGaps=True,
                       scale=scale_chart
                       )
    plt.title(title)

    fig.subplots_adjust(bottom=0.4)
    plt.tight_layout()
    plt.savefig(plot_file)
    plt.close(fig)
    del fig


if __name__ == '__main__':
    # TODO ech 2015-07-15 a lot of copy and paste, which maybe gets cleaned up if this becomes more standard

    df = read_df_from_file('/data/MBARI_merged.tsv', low_memory=False)

    # rename for nicer ordering of graphs
    df['domain_name_14'][df['domain_name_12'] == df['domain_name_14']] = 'AAsame'
    df['domain_name_12'][df.domain_name_12 == 'None'] = 'zNone'
    df['domain_name_14'][df.domain_name_14 == 'None'] = 'zNone'

    # ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
    colors = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale

    t = 'all'
    d2 = massage_data(df)
    data_file = '/shared_projects/MBARI/' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + t + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + t + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors, True)

    t = 'fuzzy'
    a = df[df['placement_type_12'] == t]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + t + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + t + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors, True)

    t = 'confident'
    a = df[df['placement_type_12'] == t]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + t + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + t + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors, True)

    t1 = 'confident'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors, True)

    t1 = 'confident'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors, True)

    t1 = 'none'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors[1:], True)

    t1 = 'none'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = massage_data(a)
    data_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_bar.pdf'
    plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    plot_data(data_file, plot_file, title, colors[1:], True)

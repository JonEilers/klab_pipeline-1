#!/usr/bin/env python

import matplotlib

matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

from matplotlib import pyplot as plt
import pandas as pd
import numpy as np

from klab.process.file_manager import read_df_from_file, write_df_to_file

from lib.stacked_bar_graph import StackedBarGrapher


def _get_and_clean_data(level):
    d = read_df_from_file('/data/MBARI_merged.tsv', low_memory=False)

    # rename for nicer ordering of graphs
    d['domain_name_14'][d[level + '_name_12'] == d[level + '_name_14']] = 'AAsame'
    d['domain_name_12'][d['domain_name_12'] == 'None'] = 'zNone'
    d['domain_name_14'][d['domain_name_14'] == 'None'] = 'zNone'
    return d


def _massage_data(df, level='domain'):
    # group, reshape and replace missing values
    b = pd.DataFrame(df.groupby([level + '_name_12', level + '_name_14']).size())
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


def _plot_data(data_file, plot_file, title, colors, scale_chart=False):
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


def _get_n_colors_in_hex(n=5):
    import colorsys
    hsv_tuples = [(c * 1.0 / n, 0.5, 0.5) for c in xrange(n)]
    hex_out = []
    for rgb in hsv_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        b = '#' + "".join(map(lambda x: chr(x).encode('hex'), rgb))
        hex_out.append(b)
    return hex_out


# uses spectrum of colors at a greater level of detail
def _generate_spectrum_set_of_graphs(level):
    df = _get_and_clean_data(level)

    d2 = _massage_data(df, level)

    num_rows = len(d2.index)
    colors = _get_n_colors_in_hex(num_rows)
    colors.insert(0, '#bfbfbf')  # start with grey color for 'same' category

    data_file = '/shared_projects/MBARI/' + level + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = level.title() + ' 2012 to 2014 Placements'
    plot_file = '/shared_projects/MBARI/' + level + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)


# not that interesting, as fuzzy contribution is swamped by confident
# keep it around in case I drill down to it for some other reason
def _generate_domain_colored_set_of_graphs_confident_fuzzy(level):
    # TODO ech 2015-07-15 a lot of copy and paste, which maybe gets cleaned up if this becomes more standard
    df = _get_and_clean_data(level)

    # ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
    colors = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale

    t = 'fuzzy'
    a = df[df['placement_type_12'] == t]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)

    t = 'confident'
    a = df[df['placement_type_12'] == t]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)

    t1 = 'confident'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)

    t1 = 'confident'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)

    t1 = 'none'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:], True)

    t1 = 'none'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:], True)


def _generate_domain_colored_set_of_graphs(level):
    df = _get_and_clean_data(level)

    # ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
    colors = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale

    # all of specific level
    t = 'all'
    d2 = _massage_data(df)
    data_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = '/shared_projects/MBARI/' + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)

    # where did new placements come from? redundant, as it is last column of above graphs
    a = df[df['domain_name_12'] == 'zNone']
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_new_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'New Placements 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_new_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + level + '_level_new_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:], True)

    # where did placements get lost from?
    a = df[df['domain_name_14'] == 'zNone']
    d2 = _massage_data(a)
    data_file = '/shared_projects/MBARI/' + level + '_level_lost_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'Lost Placements 2014'
    plot_file = '/shared_projects/MBARI/' + level + '_level_lost_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/' + level + '_level_lost_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:], True)


def _new_and_lost_placements():
    # data file was hand constructed from two others
    data_file = '/shared_projects/MBARI/domain_level/domain_level_lost_new_placements.csv'
    title = 'New and Lost Placements by Domain'
    colors = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale
    plot_file = '/shared_projects/MBARI/domain_level/domain_level_lost_new_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:])  # there are no 'Same' columns, so skip first color
    plot_file = '/shared_projects/MBARI/domain_level/domain_level_lost_new_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors[1:], True)


def _taxa_depth_histogram(df, field, title, color='green'):
    s = df[field]
    s[s == 'None'] = 0
    depths = s.values.astype(np.float)

    bins = range(0, 25, 1)
    plt.hist(depths, bins=bins, facecolor=color, normed=1)

    plt.xlabel(r'Taxa Depth')
    plt.ylabel(r'Frequency')
    plt.title(title)
    plt.grid(True)

    plt.savefig('/shared_projects/MBARI/' + field + '_histogram.pdf')


if __name__ == '__main__':
    # _generate_spectrum_set_of_graphs('domain')
    # _generate_spectrum_set_of_graphs('division')

    # _generate_domain_colored_set_of_graphs('domain')
    # _generate_domain_colored_set_of_graphs('division')
    # _generate_domain_colored_set_of_graphs('class')
    # _generate_domain_colored_set_of_graphs('lowest_classification')

    # _new_and_lost_placements()

    d = read_df_from_file('/data/MBARI_merged.tsv', low_memory=False)
    # _taxa_depth_histogram(d, 'taxa_depth_12', '2012')
    _taxa_depth_histogram(d, 'taxa_depth_14', '2014', 'blue')

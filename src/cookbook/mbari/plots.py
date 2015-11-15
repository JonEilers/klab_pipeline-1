#!/usr/bin/env python

from __future__ import division

import pandas as pd
import numpy as np
import matplotlib
from matplotlib.ticker import FuncFormatter

matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

from matplotlib import pyplot as plt

from cookbook.mbari import MBARI_ANALYSIS_DIR, MBARI_DATA_DIR, COLOR_2012, COLOR_2014
from klab.process.file_manager import read_df_from_file, write_df_to_file
from lib.stacked_bar_graph import StackedBarGrapher

MBARI_MERGED_FILE = MBARI_DATA_DIR + 'MBARI_merged.tsv'
# MBARI_MERGED_FILE = MBARI_DATA_DIR + 'mbari_test_merged.tsv'

# ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
DOMAIN_COLORS = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale


def _get_and_clean_data(level):
    d = read_df_from_file(MBARI_MERGED_FILE, low_memory=False)
    d.fillna('None', inplace=True)

    # rename for nicer ordering of graphs
    d.ix[d[level + '_name_12'] == d[level + '_name_14'], 'domain_name_14'] = 'AAsame'
    d.ix[d['domain_name_12'] == 'None', 'domain_name_12'] = 'zNone'
    d.ix[d['domain_name_14'] == 'None', 'domain_name_14'] = 'zNone'
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
    c.ix[c[''] == 'zNone', ''] = 'New Placements'
    c.ix[c[''] == 'top level', ''] = 'Top Level'
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
def _generate_euk_spectrum_set_of_graphs(level):
    df = _get_and_clean_data(level)
    t1 = 'Eukaryota'
    t2 = 'Eukaryota'
    a = df[df['domain_name_12'] == t1]
    a = a[a['domain_name_14'] == t2]

    d2 = _massage_data(a, level)

    num_rows = len(d2.index)
    colors = _get_n_colors_in_hex(num_rows)
    colors.insert(0, '#bfbfbf')  # start with grey color for 'same' category

    data_file = MBARI_ANALYSIS_DIR + level + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'Eukaryota ' + level.title() + ' 2012 to 2014 Placements'
    plot_file = MBARI_ANALYSIS_DIR + level + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, colors)
    plot_file = MBARI_ANALYSIS_DIR + level + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, colors, True)


# not that interesting, as fuzzy contribution is swamped by confident
# keep it around in case I drill down to it for some other reason
def _generate_domain_colored_set_of_graphs_confident_fuzzy(level):
    # TODO ech 2015-07-15 a lot of copy and paste, which maybe gets cleaned up if this becomes more standard
    df = _get_and_clean_data(level)

    t = 'fuzzy'
    a = df[df['placement_type_12'] == t]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)

    t = 'confident'
    a = df[df['placement_type_12'] == t]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)

    t1 = 'confident'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)

    t1 = 'confident'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)

    t1 = 'none'
    t2 = 'confident'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:])  # there are no 'Same' columns, so skip first color
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:], True)

    t1 = 'none'
    t2 = 'fuzzy'
    a = df[df['placement_type_12'] == t1.title()]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = 'No 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:])  # there are no 'Same' columns, so skip first color
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:], True)


def _generate_domain_colored_set_of_graphs(level):
    df = _get_and_clean_data(level)

    # all of specific level
    t = 'all'
    d2 = _massage_data(df)
    data_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = MBARI_ANALYSIS_DIR + level + '_level_' + t + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)


def _new_and_lost_placements():
    # data file was hand constructed from two others
    data_file = MBARI_ANALYSIS_DIR + 'domain_level/domain_level_lost_new_placements.csv'
    title = 'New and Lost Placements by Domain'
    plot_file = MBARI_ANALYSIS_DIR + 'domain_level/domain_level_lost_new_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:])  # there are no 'Same' columns, so skip first color
    plot_file = MBARI_ANALYSIS_DIR + 'domain_level/domain_level_lost_new_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:], True)


def _to_percent(y, position):
    s = str(y * 100)
    # The percent symbol needs escaping in latex
    if matplotlib.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


def _get_values_and_weights(series):
    s = series.dropna()  # drop the null values
    values = s.values.astype(np.float)  # cast series as numpy array
    weights = np.zeros_like(values) + 1 / len(values)  # calculate weights
    return values, weights


def _remove_top_right_lines_and_ticks():
    plot = plt.gca()
    plot.spines['right'].set_visible(False)
    plot.spines['top'].set_visible(False)
    plot.xaxis.set_ticks_position('bottom')
    plot.yaxis.set_ticks_position('left')


def _create_comparison_histogram(bins, series1, series2, xlabel, title, file_name, output_dir=MBARI_ANALYSIS_DIR,
                                 xlim=None, method='overlap'):
    values, weights = _get_values_and_weights(series1)
    if method == 'overlap':
        n, b, p = plt.hist(values, bins=bins, weights=weights, facecolor='b', label='2012', alpha=0.6)
    else:
        n, b, p = plt.hist(values, bins=bins, weights=weights, rwidth=0.4, facecolor=COLOR_2012, align='left',
                           label='2012')
    # print n
    # print n.sum()
    values, weights = _get_values_and_weights(series2)
    if method == 'overlap':
        n, b, p = plt.hist(values, bins=bins, weights=weights, facecolor='r', label='2014', alpha=0.6)
    else:
        n, b, p = plt.hist(values, bins=bins, weights=weights, rwidth=0.4, facecolor=COLOR_2014, align='mid',
                           label='2014')
    # print n
    # print n.sum()
    # print '======='

    plt.gca().yaxis.set_major_formatter(FuncFormatter(_to_percent))
    plt.xlabel(xlabel)
    plt.title(title)
    if xlim:
        plt.xlim(xlim)
    plt.grid(True)
    _remove_top_right_lines_and_ticks()
    plt.legend(bbox_to_anchor=(0.9, 0.9))

    plt.savefig(output_dir + file_name)
    plt.close()


def _create_taxa_depth_histogram(df12, df14, domain_filter):
    bins = range(0, 25, 1)
    file_name = domain_filter.lower() + '_taxa_depth_histogram.pdf'
    _create_comparison_histogram(bins=bins, series1=df12.taxa_depth, series2=df14.taxa_depth, xlabel=r'Taxa Depth',
                                 title=domain_filter + r' Taxa Depth per Year', xlim=[0, 25], file_name=file_name,
                                 output_dir=MBARI_ANALYSIS_DIR + 'taxa_depth_histograms/')


def _create_edpl_histogram(df12, df14, domain_filter):
    bin_width = 0.04
    bins = np.arange(0, 1 + bin_width, bin_width)
    file_name = domain_filter.lower() + '_edpl_histogram.pdf'
    _create_comparison_histogram(bins=bins, series1=df12.edpl, series2=df14.edpl,
                                 xlabel=r'Expected Distance between Placement Locations',
                                 title=domain_filter + r' EDPL per Year', xlim=[-0.02, 1], file_name=file_name,
                                 output_dir=MBARI_ANALYSIS_DIR + 'edpl_histograms/')


def _create_lwr_histogram(df12, df14, domain_filter):
    bin_width = 0.04
    bins = np.arange(0, 1 + bin_width, bin_width)
    file_name = domain_filter.lower() + '_lwr_histogram.pdf'
    _create_comparison_histogram(bins=bins, series1=df12.like_weight_ratio, series2=df14.like_weight_ratio,
                                 xlabel=r'Like Weight Ratio', title=domain_filter + r' LWR per Year', xlim=[0, 1],
                                 file_name=file_name, output_dir=MBARI_ANALYSIS_DIR + 'lwr_histograms/')


def _create_post_prob_histogram(df12, df14, domain_filter):
    bin_width = 0.04
    bins = np.arange(0, 1 + bin_width, bin_width)
    file_name = domain_filter.lower() + '_post_prob_histogram.pdf'
    _create_comparison_histogram(bins=bins, series1=df12.post_prob, series2=df14.post_prob,
                                 xlabel=r'Posterior Probability',
                                 title=domain_filter + r' Posterior Probability per Year', xlim=[0, 1],
                                 file_name=file_name, output_dir=MBARI_ANALYSIS_DIR + 'post_prob_histograms/')


def create_stacked_charts():
    _generate_domain_colored_set_of_graphs('domain')
    _new_and_lost_placements()
    # _generate_domain_colored_set_of_graphs('division')
    # _generate_domain_colored_set_of_graphs('class')
    # _generate_domain_colored_set_of_graphs('lowest_classification')


def create_histograms(domain_filter='All'):
    d12 = read_df_from_file(MBARI_DATA_DIR + '2012_MBARI_cog_placements_with_lineage.tsv', low_memory=False)
    d14 = read_df_from_file(MBARI_DATA_DIR + '2014_MBARI_cog_placements_with_lineage.tsv', low_memory=False)
    if domain_filter != 'All':
        d12 = d12[d12.domain_name == domain_filter]
        d14 = d14[d14.domain_name == domain_filter]

    _create_lwr_histogram(d12, d14, domain_filter)
    _create_post_prob_histogram(d12, d14, domain_filter)
    _create_taxa_depth_histogram(d12, d14, domain_filter)
    _create_edpl_histogram(d12, d14, domain_filter)


if __name__ == '__main__':
    # _generate_euk_spectrum_set_of_graphs('division')

    # create_stacked_charts()
    create_histograms()
    create_histograms('Eukaryota')
    create_histograms('Bacteria')

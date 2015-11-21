#!/usr/bin/env python

from __future__ import division

import os

import pandas as pd
import numpy as np
import matplotlib as mpl

mpl.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

from matplotlib import pyplot as plt
from matplotlib import rcParams
from matplotlib.ticker import FuncFormatter

from klab.process.file_manager import read_df_from_file, write_df_to_file
from klab.process.derived_info import CONFIDENT, FUZZY
from lib.stacked_bar_graph import StackedBarGrapher
from cookbook.mbari import MBARI_ANALYSIS_DIR, MBARI_DATA_DIR, COLOR_2012, COLOR_2014, MBARI_12_14_MERGED_FILE, \
    MBARI_2012_LINEAGE_FILE, MBARI_2014_LINEAGE_FILE


# MBARI_12_14_MERGED_FILE = MBARI_DATA_DIR + 'mbari_test_merged.tsv'

# ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Viruses', 'Top Level', 'New']
DOMAIN_COLORS = ['0.75', 'y', 'g', 'b', 'r', 'c', 'k']  # number is grey scale


def _ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def _get_and_clean_data(level):
    d = read_df_from_file(MBARI_12_14_MERGED_FILE, low_memory=False)
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


def _mbari_file_path(level):
    return MBARI_ANALYSIS_DIR + 'figure_2/' + level + '_level_'


# not that interesting, as fuzzy contribution is swamped by confident
# keep it around in case I drill down to it for some other reason
def _generate_domain_colored_set_of_graphs_confident_fuzzy(level):
    df = _get_and_clean_data(level)
    file_path = _mbari_file_path(level)

    t1 = CONFIDENT
    t2 = FUZZY
    a = df[df['placement_type_12'] == t1]
    a = a[a['placement_type_14'] == t2]
    d2 = _massage_data(a)
    data_file = file_path + t1 + '_' + t2 + '_placements.csv'
    write_df_to_file(d2, data_file)
    title = t1.title() + ' 2012 Placements to ' + t2.title() + ' 2014'
    plot_file = file_path + t1 + '_' + t2 + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = file_path + t1 + '_' + t2 + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)


def _generate_domain_colored_set_of_graphs(level):
    df = _get_and_clean_data(level)
    t = 'all'  # all of specific level
    file_path = _mbari_file_path(level) + t
    d2 = _massage_data(df)
    data_file = file_path + '_placements.csv'
    _ensure_dir(data_file)
    write_df_to_file(d2, data_file)
    title = t.title() + ' 2012 Placements to 2014'
    plot_file = file_path + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS)
    plot_file = file_path + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS, True)


def _new_and_lost_placements(level):
    t = 'new_and_lost'
    file_path = _mbari_file_path(level) + t
    # data file was hand constructed from two others
    data_file = file_path + '_placements.csv'
    title = 'New and Lost Placements by Domain'
    plot_file = file_path + '_placements_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:])  # there are no 'Same' columns, so skip first color
    plot_file = file_path + '_placements_scaled_bar.pdf'
    _plot_data(data_file, plot_file, title, DOMAIN_COLORS[1:], True)


def _to_percent(y, position):
    s = str(y * 100).split('.')[0]  # only take integer part
    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


def _get_values_and_weights(series):
    s = series.dropna()  # drop the null values
    values = s.values.astype(np.float)  # cast series as numpy array
    weights = np.zeros_like(values) + 1 / len(values)  # calculate weights
    return values, weights


def _adjust_ticks_and_labels(plot=plt.gca()):
    plot.tick_params(
        axis='both',  # changes apply to the x-axis
        which='both',  # both major and minor ticks are affected
        length=0,  # length of tick is 0 - turn them all off
    )
    plot.tick_params(axis='x', labelsize=8)
    plot.tick_params(axis='y', labelsize=8)


def _create_comparison_histogram(a, bins, series1, series2, xlabel, title=None, xlim=None, ylim=None, method='overlap'):
    values, weights = _get_values_and_weights(series1)
    if method == 'overlap':
        a.hist(values, bins=bins, weights=weights, facecolor=COLOR_2012, label='2012', alpha=0.5)
    else:
        a.hist(values, bins=bins, weights=weights, facecolor=COLOR_2012, label='2012', rwidth=0.4, align='left')
    values, weights = _get_values_and_weights(series2)
    if method == 'overlap':
        a.hist(values, bins=bins, weights=weights, facecolor=COLOR_2014, label='2014', alpha=0.5)
    else:
        a.hist(values, bins=bins, weights=weights, facecolor=COLOR_2012, label='2014', rwidth=0.4, align='mid')

    a.yaxis.set_major_formatter(FuncFormatter(_to_percent))
    a.set_xlabel(xlabel)
    if title:
        a.set_title(title)
    if xlim:
        a.set_xlim(xlim)
    if ylim:
        a.set_ylim(ylim)
    a.grid(True)


def _create_taxa_depth_histogram(a, df12, df14):
    bins = range(0, 25, 1)
    _create_comparison_histogram(a, bins=bins, series1=df12.taxa_depth, series2=df14.taxa_depth, xlabel=r'Taxa Depth',
                                 xlim=[0, 25])


def _create_edpl_histogram(a, df12, df14):
    min_lim = 0
    max_lim = 2  # manual range (clips a long tail with few values)
    num_bins = 40
    bin_width = (max_lim - min_lim) / num_bins
    bins = np.arange(min_lim, max_lim + bin_width, bin_width)
    _create_comparison_histogram(a, bins=bins, series1=df12.edpl, series2=df14.edpl, xlabel=r'EDPL',
                                 xlim=[min_lim, max_lim], ylim=[0, 0.5])


def _create_post_prob_histogram(a, df12, df14, title):
    bin_width = 0.04
    bins = np.arange(0, 1 + bin_width, bin_width)
    _create_comparison_histogram(a, bins=bins, series1=df12.post_prob, series2=df14.post_prob,
                                 xlabel=r'Posterior Probability', xlim=[0, 1], ylim=[0, 0.25], title=title)


def create_edpl_post_prob_scatter(year, domain_filter='All', bins=100):
    df = read_df_from_file(MBARI_DATA_DIR + year + '_MBARI_cog_placements_with_lineage.tsv')
    if domain_filter != 'All':
        df = df[df.domain_name == domain_filter]
    # bin on posterior probability
    df['bin'] = pd.cut(df.post_prob, bins)
    d = df.groupby('bin').agg({'post_prob': [np.size, np.mean], 'edpl': [np.mean]})
    plt.scatter(d['post_prob', 'mean'], d['edpl', 'mean'], c='cyan')
    plt.title(year + ' ' + domain_filter.title())
    plt.ylim(-0.025, 1.025)
    plt.xlabel('Posterior Probability (' + str(bins) + ' bins)')
    plt.xlim(-0.025, 1.025)
    plt.ylabel('EDPL')
    # _remove_top_right_lines_and_ticks()

    out_file = MBARI_ANALYSIS_DIR + 'figure_4/' + year + '_' + domain_filter.lower() + '_edpl_pp_scatter.pdf'
    _ensure_dir(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 1 is three bar charts: ref pkg counts, placement counts, normalized counts
def create_figure_1():
    pass


# Figure 2 is four bar charts: (stacked, scaled) x (domain, lowest_classification)
def create_figure_2():
    _generate_domain_colored_set_of_graphs('domain')
    _new_and_lost_placements('domain')
    _generate_domain_colored_set_of_graphs('lowest_classification')


# Figure 3 is six histograms: (post_prob, edpl, taxa_depth) x (euks, bacteria)
def create_figure_3():
    # MBARI_2012_LINEAGE_FILE = MBARI_DATA_DIR + '2012_MBARI_cog_placements_with_lineage_test.tsv'
    # MBARI_2014_LINEAGE_FILE = MBARI_DATA_DIR + '2014_MBARI_cog_placements_with_lineage_test.tsv'
    df12 = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    df14 = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    f, axarr = plt.subplots(3, 2)

    domain_filter = 'Eukaryota'
    d12 = df12[df12.domain_name == domain_filter]
    d14 = df14[df14.domain_name == domain_filter]
    _create_post_prob_histogram(axarr[0, 0], d12, d14, domain_filter)
    _create_edpl_histogram(axarr[1, 0], d12, d14)
    _create_taxa_depth_histogram(axarr[2, 0], d12, d14)

    domain_filter = 'Bacteria'
    d12 = df12[df12.domain_name == domain_filter]
    d14 = df14[df14.domain_name == domain_filter]
    _create_post_prob_histogram(axarr[0, 1], d12, d14, domain_filter)
    _create_edpl_histogram(axarr[1, 1], d12, d14)
    _create_taxa_depth_histogram(axarr[2, 1], d12, d14)

    # put legend in lower right subplot
    axarr[2, 1].legend(bbox_to_anchor=(0.95, 0.95))
    # hide y-tick labels
    plt.setp(axarr[0, 1].get_yticklabels(), visible=False)
    plt.setp(axarr[1, 1].get_yticklabels(), visible=False)
    # hide top and right ticks for all subplots
    [_adjust_ticks_and_labels(axarr[x, y]) for x in range(3) for y in range(2)]

    plt.tight_layout()

    out_file = MBARI_ANALYSIS_DIR + 'figure_3.pdf'
    _ensure_dir(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 4 is two scatterplots: (edpl/post_prob) x (euks, bacteria)
def create_figure_4():
    create_edpl_post_prob_scatter('2012', 'Eukaryota')
    create_edpl_post_prob_scatter('2014', 'Eukaryota')
    create_edpl_post_prob_scatter('2012', 'Bacteria')
    create_edpl_post_prob_scatter('2014', 'Bacteria')


if __name__ == '__main__':
    # create_figure_1()

    # create_figure_2()

    # create_figure_4()

    plt.style.use('ggplot')
    rcParams['xtick.direction'] = 'in'  # even turned off, they take space, so reduce that by directing in
    rcParams['ytick.direction'] = 'in'
    create_figure_3()

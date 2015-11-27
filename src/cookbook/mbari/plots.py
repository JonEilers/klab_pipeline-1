#!/usr/bin/env python

from __future__ import division

import os

import numpy as np
import pandas as pd
import matplotlib as mpl

mpl.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter

from klab.process.file_manager import read_df_from_file, write_df_to_file
from klab.process.derived_info import group_and_count
from cookbook.mbari import MBARI_ANALYSIS_DIR, COLOR_2012, COLOR_2014, MBARI_12_14_MERGED_FILE, \
    MBARI_2012_LINEAGE_FILE, MBARI_2014_LINEAGE_FILE

# ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Lost Placements']
DOMAIN_COLORS = ['0.75', 'y', 'g', 'b', 'k']  # number is grey scale


def _ensure_directory_exists(f):
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
    c.rename(columns={'AAsame': 'Same', 'top level': 'Top Level', 'zNone': 'Lost Placements'}, inplace=True)

    # clean up row names
    c.ix[c[''] == 'zNone', ''] = 'New Placements'
    c.ix[c[''] == 'top level', ''] = 'Top Level'
    c.columns.name = ''
    c.set_index([''], inplace=True)  # set index to first column
    return c


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
    # title = 'Eukaryota ' + level.title() + ' 2012 to 2014 Placements'
    # plot_file = MBARI_ANALYSIS_DIR + level + '_placements_bar.pdf'
    # _plot_data(data_file, plot_file, title, colors)
    # plot_file = MBARI_ANALYSIS_DIR + level + '_placements_scaled_bar.pdf'
    # _plot_data(data_file, plot_file, title, colors, True)


def _generate_domain_stack_plots(sp1, sp2, level):
    df = _get_and_clean_data(level)
    d = _massage_data(df)
    a = d['Lost Placements'].tolist()
    a.insert(0, 0.0)
    d.loc['Lost Placements'] = a
    d.drop('Lost Placements', axis=1, inplace=True)
    categories = d.index.tolist()  # index is list of categories

    d.plot(ax=sp1, kind='bar', stacked=True, color=DOMAIN_COLORS, width=0.95, linewidth=0.0, edgecolor='white')
    sp1.set_xticklabels(categories, rotation='horizontal')
    sp1.set_title('2012 to 2014 Placements')

    d = d.div(d.sum(axis=1), axis=0)  # scale the data
    d.plot(ax=sp2, kind='bar', stacked=True, color=DOMAIN_COLORS, width=0.95, linewidth=0.0, edgecolor='white')
    sp2.set_xticklabels(categories, rotation='horizontal')
    sp2.set_title('2012 to 2014 Placements')
    sp2.yaxis.set_major_formatter(FuncFormatter(_to_percent))


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


def _create_comparison_histogram(subplot, bins, series1, color1, series2, color2, xlabel, xlim=None, ylim=None):
    values, weights = _get_values_and_weights(series1)
    subplot.hist(values, bins=bins, weights=weights, facecolor=color1, label='2012', alpha=0.5,
                 linewidth=0.5, edgecolor='white')
    values, weights = _get_values_and_weights(series2)
    subplot.hist(values, bins=bins, weights=weights, facecolor=color2, label='2014', alpha=0.5,
                 linewidth=0.5, edgecolor='white')

    subplot.yaxis.set_major_formatter(FuncFormatter(_to_percent))
    subplot.set_xlabel(xlabel, fontsize=10)
    if xlim:
        subplot.set_xlim(xlim)
    if ylim:
        subplot.set_ylim(ylim)
    subplot.tick_params(axis='x', labelsize=8)
    subplot.tick_params(axis='y', labelsize=8)


def _create_taxa_depth_histogram(a, df12, df14):
    bins = range(0, 25, 1)
    _create_comparison_histogram(a, bins=bins, series1=df12.taxa_depth, color1=COLOR_2012, series2=df14.taxa_depth,
                                 color2=COLOR_2014, xlabel=r'Taxa Depth', xlim=[0, 25])


def _create_edpl_histogram(a, df12, df14):
    min_lim = 0
    max_lim = 1.2  # manual range (clips a long tail with few values)
    num_bins = 40
    bin_width = (max_lim - min_lim) / num_bins
    bins = np.arange(min_lim, max_lim + bin_width, bin_width)
    _create_comparison_histogram(a, bins=bins, series1=df12.edpl, color1=COLOR_2012, series2=df14.edpl,
                                 color2=COLOR_2014, xlabel=r'EDPL', xlim=[min_lim, max_lim], ylim=[0, 0.45])


def _create_post_prob_histogram(a, df12, df14):
    bin_width = 0.04
    bins = np.arange(0, 1 + bin_width, bin_width)
    _create_comparison_histogram(a, bins=bins, series1=df12.post_prob, color1=COLOR_2012, series2=df14.post_prob,
                                 color2=COLOR_2014, xlabel=r'Posterior Probability', xlim=[0, 1], ylim=[0, 0.25])


def create_edpl_post_prob_scatter(subplot, df, year, color, domain_filter, bins=100):
    d1 = df[df.domain_name == domain_filter].copy()
    # bin on posterior probability
    d1['bin'] = pd.cut(d1.post_prob, bins)
    d = d1.groupby('bin').agg({'post_prob': [np.size, np.mean], 'edpl': [np.mean]})

    subplot.scatter(d['post_prob', 'mean'], d['edpl', 'mean'], c=color, label=year, alpha=0.8)
    subplot.set_title(domain_filter.title())
    subplot.set_ylim(-0.025, 1.025)
    subplot.set_xlabel('Posterior Probability')
    subplot.set_xlim(-0.025, 1.025)
    subplot.set_ylabel('EDPL')


def _side_by_side_bar(subplot, df, x, y, colors, gap=None):
    categories = df[x].unique()
    n = len(categories)
    bars = len(y)
    if not gap:
        gap = width = 1 / (bars + 1)
    else:  # this path needs work
        width = (1 - gap) / bars
    width += 0.005  # leave slight space between bars
    alpha = 0.6
    xticks = range(1, n + 1)

    for i in range(0, bars):
        pos = [x - (1 - gap) / 2. + i * width for x in xticks]
        subplot.bar(pos, df[y[i]], gap, color=colors[i], label=y[i], alpha=alpha, linewidth=0)
    subplot.set_xticks(xticks)
    subplot.set_xticklabels(categories)
    subplot.tick_params(axis='x', labelsize=8)
    subplot.tick_params(axis='y', labelsize=8)


# Figure 1 is three bar charts: ref pkg counts, placement counts, normalized counts
def create_figure_1():
    fig, axes = plt.subplots(nrows=3, ncols=1)
    x = 'domain_name'
    y = ['2012', '2014']
    c = [COLOR_2012, COLOR_2014]

    d3 = read_df_from_file('/Users/ehervol/Projects/WWU/MBARI_data/mbari_ref_counts.tsv')
    subplot = axes[0]
    subplot.set_title('Unique Reference Sequences by Domain')
    _side_by_side_bar(subplot, d3, x=x, y=y, colors=c)

    # MBARI_2012_LINEAGE_FILE = MBARI_DATA_DIR + '2012_MBARI_cog_placements_with_lineage_test.tsv'
    # MBARI_2014_LINEAGE_FILE = MBARI_DATA_DIR + '2014_MBARI_cog_placements_with_lineage_test.tsv'
    # filter by domain and drop dups for 2012 and 2014 data
    d = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    d.drop_duplicates('classification', inplace=True)
    df = d[d['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df12 = group_and_count(df, ['domain_name'])
    d = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    d.drop_duplicates('classification', inplace=True)
    df = d[d['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df14 = group_and_count(df, ['domain_name'])
    # merge 2012 and 2014 data
    df = pd.merge(df12, df14, on='domain_name', how='outer', suffixes=('_12', '_14'))
    df.rename(columns={'count_12': '2012', 'count_14': '2014'}, inplace=True)

    subplot = axes[1]
    subplot.set_title('Unique Placements by Domain')
    _side_by_side_bar(subplot, df, x=x, y=y, colors=c)

    # normalize data
    d = pd.merge(d3, df, on='domain_name', how='outer', suffixes=('_ref', '_domain'))
    d['2012'] = d['2012_domain'] / d['2012_ref']
    d['2014'] = d['2014_domain'] / d['2014_ref']

    subplot = axes[2]
    subplot.set_title('Normalized Placements by Domain')
    _side_by_side_bar(subplot, d, x=x, y=y, colors=c)

    # put legend in lower right subplot and set font size
    legend = axes[0].legend(loc='upper right')
    plt.setp(legend.get_texts(), fontsize=10)
    # hide x-tick labels for a couple subplots
    plt.setp(axes[0].get_xticklabels(), visible=False)
    plt.setp(axes[1].get_xticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

    out_file = MBARI_ANALYSIS_DIR + 'figure_1.pdf'
    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 2 is four bar charts: (stacked, scaled) x (domain, lowest_classification)
def create_figure_2():
    fig, axes = plt.subplots(nrows=2, ncols=2)

    _generate_domain_stack_plots(axes[0, 0], axes[1, 0], 'domain')
    _generate_domain_stack_plots(axes[0, 1], axes[1, 1], 'lowest_classification')

    # hide x-tick labels for top subplots
    plt.setp(axes[0, 0].get_xticklabels(), visible=False)
    plt.setp(axes[0, 1].get_xticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

    out_file = MBARI_ANALYSIS_DIR + 'figure_2.pdf'
    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 3 is six histograms: (post_prob, edpl, taxa_depth) x (euks, bacteria)
def create_figure_3():
    # MBARI_2012_LINEAGE_FILE = MBARI_DATA_DIR + '2012_MBARI_cog_placements_with_lineage_test.tsv'
    # MBARI_2014_LINEAGE_FILE = MBARI_DATA_DIR + '2014_MBARI_cog_placements_with_lineage_test.tsv'
    df12 = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    df14 = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    fig, axes = plt.subplots(nrows=3, ncols=2)

    domain_filter = 'Bacteria'
    d12 = df12[df12.domain_name == domain_filter]
    d14 = df14[df14.domain_name == domain_filter]
    axes[0, 0].set_title(domain_filter)
    _create_post_prob_histogram(axes[0, 0], d12, d14)
    _create_edpl_histogram(axes[1, 0], d12, d14)
    _create_taxa_depth_histogram(axes[2, 0], d12, d14)

    domain_filter = 'Eukaryota'
    d12 = df12[df12.domain_name == domain_filter]
    d14 = df14[df14.domain_name == domain_filter]
    axes[0, 1].set_title(domain_filter)
    _create_post_prob_histogram(axes[0, 1], d12, d14)
    _create_edpl_histogram(axes[1, 1], d12, d14)
    _create_taxa_depth_histogram(axes[2, 1], d12, d14)

    # put legend in lower right subplot and set font size
    legend = axes[2, 1].legend(loc='upper right')
    plt.setp(legend.get_texts(), fontsize=10)
    # hide y-tick labels for a couple subplots
    plt.setp(axes[0, 1].get_yticklabels(), visible=False)
    plt.setp(axes[1, 1].get_yticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

    out_file = MBARI_ANALYSIS_DIR + 'figure_3.pdf'
    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


def _calc_split(df, divider, domain_filter):
    d1 = df[df.domain_name == domain_filter].copy()
    d1['bin'] = pd.cut(d1.post_prob, [0, divider, 1])
    d = d1.groupby('bin').agg({'post_prob': [np.size]})
    tot = d['post_prob', 'size'].sum()
    l = d['post_prob', 'size'][0] / tot
    r = d['post_prob', 'size'][1] / tot
    return l, r


# Figure 4 is two scatterplots: (edpl/post_prob) x (euks, bacteria)
def create_figure_4():
    df12 = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    df14 = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    fig, axes = plt.subplots(nrows=2, ncols=1)

    subplot = axes[0]
    domain_filter = 'Bacteria'
    create_edpl_post_prob_scatter(subplot, df12, '2012', COLOR_2012, domain_filter)
    create_edpl_post_prob_scatter(subplot, df14, '2014', COLOR_2014, domain_filter)

    divider_x = 0.28  # eyeballed estimate
    subplot.vlines(x=divider_x, ymin=0, ymax=1, colors='k', linestyles='dashed', label='')
    l12, r12 = _calc_split(df12, divider_x, domain_filter)
    l14, r14 = _calc_split(df14, divider_x, domain_filter)
    subplot.text(0.12, 0.81, '{:2.0f}%'.format(l12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.65, 0.81, '{:2.0f}%'.format(r12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.12, 0.68, '{:2.0f}%'.format(l14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.65, 0.68, '{:2.0f}%'.format(r14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)

    subplot = axes[1]
    domain_filter = 'Eukaryota'
    create_edpl_post_prob_scatter(subplot, df12, '2012', COLOR_2012, domain_filter)
    create_edpl_post_prob_scatter(subplot, df14, '2014', COLOR_2014, domain_filter)

    divider_x = 0.75  # eyeballed estimate
    subplot.vlines(x=divider_x, ymin=0, ymax=1, colors='k', linestyles='dashed', label='')
    l12, r12 = _calc_split(df12, divider_x, domain_filter)
    l14, r14 = _calc_split(df14, divider_x, domain_filter)
    subplot.text(0.45, 0.81, '{:2.0f}%'.format(l12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.85, 0.81, '{:2.0f}%'.format(r12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.45, 0.68, '{:2.0f}%'.format(l14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.85, 0.68, '{:2.0f}%'.format(r14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)

    # put legend in upper right subplot and set font size
    legend = axes[0].legend(loc='upper right')
    plt.setp(legend.get_texts(), fontsize=12)
    # hide x-tick labels for top subplot
    # plt.setp(axes[0].get_xticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

    out_file = MBARI_ANALYSIS_DIR + 'figure_4.pdf'
    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


if __name__ == '__main__':
    style_overrides = {
        'text.color': '0.1',  # not quite black
        'axes.labelcolor': '0.3',  # lighter grey than text
        'xtick.color': '0.4',  # lighter grey than text or label
        'ytick.color': '0.4',
        'axes.facecolor': '0.92',  # similar to ggplot
        'legend.frameon': True,  # good when gridlines are on - separates legend from background
    }
    sns.set_style('darkgrid', style_overrides)

    create_figure_1()

    create_figure_2()

    create_figure_3()

    create_figure_4()

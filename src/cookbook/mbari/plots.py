#!/usr/bin/env python

from __future__ import division, unicode_literals

import os

import matplotlib as mpl
import numpy as np
import pandas as pd

mpl.use('Agg')  # Must be before importing matplotlib.pyplot or pylab

import seaborn as sns

from matplotlib import pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib import gridspec

from klab.process.file_manager import read_df_from_file, CLASSIFICATION_COLUMN
from klab.process.derived_info import group_and_count
from cookbook.mbari import MBARI_RESULTS_DIR, COLOR_2012, COLOR_2014, COLOR_2016, MBARI_2012_LINEAGE_FILE, \
    MBARI_2014_LINEAGE_FILE, MBARI_2016_LINEAGE_FILE, MBARI_12_16_MERGED_FILE, MBARI_12_14_MERGED_FILE, \
    MBARI_12_14_REF_COUNTS_FILE

# ['Same', 'Archaea', 'Bacteria', 'Eukaryota', 'Lost Placements']
DOMAIN_COLORS = ['0.7', 'y', 'g', 'b', 'k']  # number is grey scale


def _ensure_directory_exists(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)


def _get_and_clean_data(level, file_name, label_a, label_b):
    d = read_df_from_file(file_name=file_name, low_memory=False)
    d.fillna('None', inplace=True)

    # rename for nicer ordering of graphs
    d.ix[d[level + '_name_' + label_a] == d[level + '_name_' + label_b], 'domain_name_' + label_b] = 'AAsame'
    d.ix[d['domain_name_' + label_a] == 'None', 'domain_name_' + label_a] = 'zNone'
    d.ix[d['domain_name_' + label_b] == 'None', 'domain_name_' + label_b] = 'zNone'
    return d


def _massage_data(df, label_a, label_b):
    # group, reshape and replace missing values
    b = pd.DataFrame(df.groupby(['domain_name_' + label_a, 'domain_name_' + label_b]).size())
    c = b.unstack()
    c.fillna(0, inplace=True)  # replace NaN

    # clean up column names
    c.reset_index(inplace=True)
    c.columns = c.columns.get_level_values(1)
    c.rename(columns={'AAsame': 'Same', 'top level': 'Top Level', 'zNone': 'Lost'}, inplace=True)

    # clean up row names
    c.ix[c[''] == 'zNone', ''] = '20%s New' % label_b
    c.ix[c[''] == 'top level', ''] = 'Top Level'
    c.columns.name = ''
    c.set_index([''], inplace=True)  # set index to first column

    # make last column into last row
    a = c['Lost'].tolist()
    a.insert(0, 0.0)  # pad first value with a zero
    c.loc['20%s Lost' % label_b] = a
    c.drop('Lost', axis=1, inplace=True)
    return c


def _get_n_colors_in_hex(n=5):
    import colorsys
    hsv_tuples = [(c * 1.0 / n, 0.5, 0.5) for c in range(n)]
    hex_out = []
    for rgb in hsv_tuples:
        rgb = map(lambda x: int(x * 255), colorsys.hsv_to_rgb(*rgb))
        b = '#' + "".join(map(lambda x: chr(x).encode('hex'), rgb))
        hex_out.append(b)
    return hex_out


# # uses spectrum of colors at a greater level of detail
# def _generate_euk_spectrum_set_of_graphs(level):
#     df = _get_and_clean_data(level)
#     t1 = 'Eukaryota'
#     t2 = 'Eukaryota'
#     a = df[df['domain_name_12'] == t1]
#     a = a[a['domain_name_14'] == t2]
#
#     d2 = _massage_data(a, level)
#
#     num_rows = len(d2.index)
#     colors = _get_n_colors_in_hex(num_rows)
#     colors.insert(0, '#bfbfbf')  # start with grey color for 'same' category
#
#     data_file = MBARI_RESULTS_DIR + level + '_placements.csv'
#     write_df_to_file(d2, data_file)
# title = 'Eukaryota ' + level.title() + ' 2012 to 2014 Placements'
# plot_file = MBARI_ANALYSIS_DIR + level + '_placements_bar.pdf'
# _plot_data(data_file, plot_file, title, colors)
# plot_file = MBARI_ANALYSIS_DIR + level + '_placements_scaled_bar.pdf'
# _plot_data(data_file, plot_file, title, colors, True)


def _generate_domain_stack_plot(sp1, level):
    df14 = _get_and_clean_data(level, file_name=MBARI_12_14_MERGED_FILE, label_a='12', label_b='14')
    d14 = _massage_data(df14, label_a='12', label_b='14')
    d14.drop(d14.head(3).index, inplace=True)  # drop first three rows (Arch, Bact, Euk)
    df16 = _get_and_clean_data(level, file_name=MBARI_12_16_MERGED_FILE, label_a='12', label_b='16')
    d16 = _massage_data(df16, label_a='12', label_b='16')
    d16.drop(d16.head(3).index, inplace=True)  # drop first three rows (Arch, Bact, Euk)
    d = pd.concat([d14, d16])

    d.drop('Same', axis=1, inplace=True)  # drop 'Same" column
    colors = DOMAIN_COLORS[1:]

    categories = d.index.tolist()  # index is list of categories
    width = 0.92
    gap = 1 - width
    xlim = [0 - gap - (width / 2), len(categories) - (width / 2)]  # leave gap on left edge, gap on right edge

    d.plot(ax=sp1, kind='bar', stacked=True, color=colors, width=width, linewidth=0, legend=False, alpha=0.9)
    sp1.set_xticklabels(categories, rotation='horizontal')
    sp1.set_ylabel('Placements (thousands)', color='0.4')
    sp1.yaxis.set_major_formatter(FuncFormatter(_to_thousands))
    sp1.set_xlim(xlim)
    sp1.xaxis.grid(False)


def _generate_domain_stack_and_scale_plots(sp1, sp2, level):
    df = _get_and_clean_data(level, file_name=MBARI_12_14_MERGED_FILE, label_a='12', label_b='14')
    d = _massage_data(df, label_a='12', label_b='14')
    if level != 'domain':
        d.drop(d.tail(2).index, inplace=True)  # drop last two rows if not domain level (redundant in all others)

    categories = d.index.tolist()  # index is list of categories
    width = 0.92
    gap = 1 - width
    xlim = [0 - gap - (width / 2), len(categories) - (width / 2)]  # leave gap on left edge, gap on right edge

    d.plot(ax=sp1, kind='bar', stacked=True, color=DOMAIN_COLORS, width=width, linewidth=0, legend=False, alpha=0.9)
    sp1.set_xticklabels(categories, rotation='horizontal')
    sp1.set_ylabel('Placements (thousands)', color='0.4')
    sp1.yaxis.set_major_formatter(FuncFormatter(_to_thousands))
    sp1.set_xlim(xlim)
    sp1.xaxis.grid(False)

    d = d.div(d.sum(axis=1), axis=0)  # scale the data
    d.plot(ax=sp2, kind='bar', stacked=True, color=DOMAIN_COLORS, width=width, linewidth=0, legend=False, alpha=0.9)
    sp2.set_xticklabels(categories, rotation='horizontal')
    sp2.set_ylabel('Placements (scaled)', color='0.4')
    sp2.yaxis.set_major_formatter(FuncFormatter(_to_percent))
    sp2.set_xlim(xlim)
    sp2.xaxis.grid(False)


def _to_percent(y, position):
    s = str(y * 100).split('.')[0]  # only take integer part
    # The percent symbol needs escaping in latex
    if mpl.rcParams['text.usetex'] is True:
        return s + r'$\%$'
    else:
        return s + '%'


def _to_thousands(y, position):
    s = str(y / 1000).split('.')[0]  # only take integer part
    return s


def _get_values_and_weights(series):
    s = series.dropna()  # drop the null values
    values = s.values.astype(np.float)  # cast series as numpy array
    weights = np.zeros_like(values) + 1 / len(values)  # calculate weights
    return values, weights


def _create_comparison_histogram(subplot, bins, series1, color1, series2, color2, xlabel, xlim=None, ylim=None):
    values, weights = _get_values_and_weights(series1)
    n, b, p = subplot.hist(values, bins=bins, weights=weights, facecolor=color1, label='2012', alpha=0.5,
                           linewidth=0.5, edgecolor='white')
    print('2012 ' + series1.name)
    print('{:2.3f}%'.format((1 - n.sum()) * 100))
    values, weights = _get_values_and_weights(series2)
    n, b, p = subplot.hist(values, bins=bins, weights=weights, facecolor=color2, label='2014', alpha=0.5,
                           linewidth=0.5, edgecolor='white')
    print('2014 ' + series2.name)
    print('{:2.2f}%'.format((1 - n.sum()) * 100))

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
    max_lim = 2  # manual range (clips a long tail with few values)
    num_bins = 32
    bin_width = (max_lim - min_lim) / num_bins
    bins = np.arange(min_lim, max_lim + bin_width, bin_width)
    _create_comparison_histogram(a, bins=bins, series1=df12.edpl, color1=COLOR_2012, series2=df14.edpl,
                                 color2=COLOR_2014, xlabel=r'EDPL', xlim=[min_lim, max_lim], ylim=[0, 0.6])


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
    subplot.set_ylim(-0.025, 1.0)
    subplot.set_xlabel('Posterior Probability (bins)')
    subplot.set_xlim(-0.01, 1.01)
    subplot.set_ylabel('EDPL (bins)')


def _side_by_side_bar(subplot, df, x, y, colors, gap=None):
    categories = df[x].unique()
    n = len(categories)
    bars = len(y)
    if not gap:
        gap = width = 1 / (bars + 1)
    else:  # this path needs work
        width = (1 - gap) / bars
    width += 0.008  # leave slight space between bars
    alpha = 0.6
    xticks = range(1, n + 1)

    for i in range(0, bars):
        pos = [x - (1 - gap) / 2. + i * width for x in xticks]
        subplot.bar(pos, df[y[i]], gap, color=colors[i], label=y[i], alpha=alpha, linewidth=0)
    subplot.set_xticks(xticks)
    subplot.set_xticklabels(categories)
    subplot.xaxis.grid(False)
    subplot.tick_params(axis='x', labelsize=10)
    subplot.tick_params(axis='y', labelsize=8)


def _calc_split(df, divider, domain_filter):
    d1 = df[df.domain_name == domain_filter].copy()
    d1['bin'] = pd.cut(d1.post_prob, [0, divider, 1])
    d = d1.groupby('bin').agg({'post_prob': [np.size]})
    tot = d['post_prob', 'size'].sum()
    l = d['post_prob', 'size'][0] / tot
    r = d['post_prob', 'size'][1] / tot
    return l, r


# Figure 1 is three bar charts: ref pkg counts, placement counts, normalized counts
def create_figure_1(out_file=MBARI_RESULTS_DIR + 'figure_1.pdf'):
    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(6, 8))
    x = 'domain_name'
    y = ['2012', '2014']
    c = [COLOR_2012, COLOR_2014]

    d3 = read_df_from_file(MBARI_12_14_REF_COUNTS_FILE)
    subplot = axes[0]
    subplot.set_title('Increase in Unique References')
    d3.plot('domain_name', ['change'], ax=subplot, kind='bar', linewidth=0, legend=False, alpha=0.8)
    subplot.xaxis.grid(False)
    subplot.set_xlabel('')

    # filter by domain and drop dups for 2012 and 2014 data
    d = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    d.drop_duplicates(CLASSIFICATION_COLUMN, inplace=True)
    df = d[d['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df12 = group_and_count(df, ['domain_name'])
    d = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    d.drop_duplicates(CLASSIFICATION_COLUMN, inplace=True)
    df = d[d['domain_name'].isin(['Archaea', 'Bacteria', 'Eukaryota'])]
    df14 = group_and_count(df, ['domain_name'])
    # merge 2012 and 2014 data
    df = pd.merge(df12, df14, on='domain_name', how='outer', suffixes=('_12', '_14'))
    df.rename(columns={'count_12': '2012', 'count_14': '2014'}, inplace=True)
    df['change'] = df['2014'] / df['2012']

    subplot = axes[1]
    subplot.set_title('Increase in Unique Placements')
    df.plot('domain_name', ['change'], ax=subplot, kind='bar', linewidth=0, legend=False, alpha=0.8)
    subplot.set_ylim([0, 3.5])  # same as plot above
    subplot.xaxis.grid(False)
    subplot.set_xlabel('')

    # normalize data
    d = pd.merge(d3, df, on='domain_name', how='outer', suffixes=('_ref', '_domain'))
    d['2012'] = d['2012_domain'] / d['2012_ref']
    d['2014'] = d['2014_domain'] / d['2014_ref']

    subplot = axes[2]
    subplot.set_title('Placement Efficiency')
    _side_by_side_bar(subplot, d, x=x, y=y, colors=c)
    subplot.yaxis.set_major_formatter(FuncFormatter(_to_percent))
    legend = subplot.legend(loc='upper center')

    # set legend font size
    plt.setp(legend.get_texts(), fontsize=10)
    # hide x-tick labels for a couple subplots
    plt.setp(axes[0].get_xticklabels(), visible=False)
    plt.setp(axes[1].get_xticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 2 is one stacked bar chart: new and lost for 12->14 and 12->16
def create_figure_2(out_file=MBARI_RESULTS_DIR + 'figure_2.pdf'):
    fig, axes = plt.subplots(nrows=1, ncols=1)
    _generate_domain_stack_plot(sp1=axes, level='domain')

    legend = axes.legend(loc='upper left')
    plt.setp(legend.get_texts(), fontsize=10)
    # remove dead space
    plt.tight_layout()
    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 2 is four bar charts: (stacked, scaled) x (domain, lowest_classification)
def create_figure_2_original(out_file=MBARI_RESULTS_DIR + 'figure_2.pdf'):
    # plt.figure(figsize=(4, 6))
    gs = gridspec.GridSpec(2, 2, width_ratios=[5, 3])  # change widths (5 bars on left, 3 on right)
    ax1 = plt.subplot(gs[0, 0])
    ax2 = plt.subplot(gs[0, 1])
    ax3 = plt.subplot(gs[1, 0])
    ax4 = plt.subplot(gs[1, 1])

    _generate_domain_stack_and_scale_plots(ax1, ax3, 'domain')
    _generate_domain_stack_and_scale_plots(ax2, ax4, 'lowest_classification')

    ax1.set_title("Domain Level", fontsize=10)
    ax2.set_title("Lowest Classification Level", fontsize=10)
    # put legend in upper left subplot and set font size
    legend = ax1.legend(loc='upper right')
    plt.setp(legend.get_texts(), fontsize=10)
    # hide x-tick labels for top subplots
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    # hide y-tick labels for right subplots
    plt.setp(ax2.get_yticklabels(), visible=False)
    ax2.set_ylabel('')
    plt.setp(ax4.get_yticklabels(), visible=False)
    ax4.set_ylabel('')
    # fig.suptitle('2012 to 2014 Placement Changes')
    # plt.subplots_adjust(top=0.9)  # move subplots down to accomodate title (tight_layout doesn't consider it)
    # remove dead space
    plt.tight_layout()

    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 3 is six histograms: (post_prob, edpl, taxa_depth) x (euks, bacteria)
def create_figure_3(out_file=MBARI_RESULTS_DIR + 'figure_3.pdf'):
    df12 = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    df14 = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    fig, axes = plt.subplots(nrows=3, ncols=2)

    domain_filter = 'Bacteria'
    print(domain_filter)
    d12 = df12[df12.domain_name == domain_filter]
    d14 = df14[df14.domain_name == domain_filter]
    axes[0, 0].set_title(domain_filter)
    _create_post_prob_histogram(axes[0, 0], d12, d14)
    _create_edpl_histogram(axes[1, 0], d12, d14)
    _create_taxa_depth_histogram(axes[2, 0], d12, d14)

    domain_filter = 'Eukaryota'
    print(domain_filter)
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

    _ensure_directory_exists(out_file)
    plt.savefig(out_file)
    plt.close()


# Figure 4 is two scatterplots: (edpl/post_prob) x (euks, bacteria)
def create_figure_4(out_file=MBARI_RESULTS_DIR + 'figure_4.pdf'):
    df12 = read_df_from_file(MBARI_2012_LINEAGE_FILE, low_memory=False)
    df14 = read_df_from_file(MBARI_2014_LINEAGE_FILE, low_memory=False)
    df16 = read_df_from_file(MBARI_2016_LINEAGE_FILE, low_memory=False)
    fig, axes = plt.subplots(nrows=2, ncols=1)

    subplot = axes[0]
    domain_filter = 'Bacteria'
    create_edpl_post_prob_scatter(subplot, df12, '2012', COLOR_2012, domain_filter)
    create_edpl_post_prob_scatter(subplot, df14, '2014', COLOR_2014, domain_filter)
    create_edpl_post_prob_scatter(subplot, df16, '2016', COLOR_2016, domain_filter)

    divider_x = 0.27  # eyeballed estimate
    subplot.vlines(x=divider_x, ymin=0, ymax=1, colors='k', linestyles='dashed', label='')
    l12, r12 = _calc_split(df12, divider_x, domain_filter)
    l14, r14 = _calc_split(df14, divider_x, domain_filter)
    l16, r16 = _calc_split(df16, divider_x, domain_filter)
    subplot.text(0.12, 0.83, '{:2.0f}%'.format(l12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.65, 0.83, '{:2.0f}%'.format(r12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.12, 0.70, '{:2.0f}%'.format(l14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.65, 0.70, '{:2.0f}%'.format(r14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.12, 0.57, '{:2.0f}%'.format(l16 * 100), transform=subplot.transAxes, color=COLOR_2016, fontsize=15)
    subplot.text(0.65, 0.57, '{:2.0f}%'.format(r16 * 100), transform=subplot.transAxes, color=COLOR_2016, fontsize=15)

    subplot = axes[1]
    domain_filter = 'Eukaryota'
    create_edpl_post_prob_scatter(subplot, df12, '2012', COLOR_2012, domain_filter)
    create_edpl_post_prob_scatter(subplot, df14, '2014', COLOR_2014, domain_filter)
    create_edpl_post_prob_scatter(subplot, df16, '2016', COLOR_2014, domain_filter)

    divider_x = 0.80  # eyeballed estimate
    subplot.vlines(x=divider_x, ymin=0, ymax=1, colors='k', linestyles='dashed', label='')
    l12, r12 = _calc_split(df12, divider_x, domain_filter)
    l14, r14 = _calc_split(df14, divider_x, domain_filter)
    l16, r16 = _calc_split(df16, divider_x, domain_filter)
    subplot.text(0.45, 0.83, '{:2.0f}%'.format(l12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.85, 0.83, '{:2.0f}%'.format(r12 * 100), transform=subplot.transAxes, color=COLOR_2012, fontsize=15)
    subplot.text(0.45, 0.70, '{:2.0f}%'.format(l14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.85, 0.70, '{:2.0f}%'.format(r14 * 100), transform=subplot.transAxes, color=COLOR_2014, fontsize=15)
    subplot.text(0.45, 0.57, '{:2.0f}%'.format(l16 * 100), transform=subplot.transAxes, color=COLOR_2016, fontsize=15)
    subplot.text(0.85, 0.57, '{:2.0f}%'.format(r16 * 100), transform=subplot.transAxes, color=COLOR_2016, fontsize=15)

    # put legend in upper right subplot and set font size
    legend = axes[0].legend(loc='upper right', scatterpoints=3)
    plt.setp(legend.get_texts(), fontsize=12)
    # hide x-tick labels for top subplot
    # plt.setp(axes[0].get_xticklabels(), visible=False)
    # remove dead space
    plt.tight_layout()

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

    # create_figure_1()

    create_figure_2()

    # create_figure_3()

    create_figure_4()

    # generate figure 1 in different styles
    # styles = mpl.style.available
    # styles.insert(0, u'default')
    # for style in styles:
    #     mpl.rcParams.update(mpl.rcParamsDefault)
    #     if style != 'default':
    #         plt.style.use(style)
    #     create_figure_1(MBARI_ANALYSIS_DIR + 'styles/figure1_mpl_' + style + '.pdf')

    # for reasons not worth going into, have to run the mpl and sns code separately
    # sns_styles = ('darkgrid', 'whitegrid', 'dark', 'white', 'ticks')
    # for style in sns_styles:
    #     sns.set_style(style)
    #     create_figure_1(MBARI_ANALYSIS_DIR + 'styles/figure1_sns_' + style + '.pdf')

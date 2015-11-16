#!/usr/bin/env python

from __future__ import division

import matplotlib
import pandas as pd

from klab.process.derived_info import add_placement_type_column
from klab.process.file_manager import read_df_from_file, write_df_to_file
from cookbook.mbari import MBARI_ANALYSIS_DIR, MBARI_2012_LINEAGE_FILE, MBARI_2014_LINEAGE_FILE

matplotlib.use('Agg')  # Must be before importing matplotlib.pyplot or pylab
import matplotlib.pyplot as plt


# 2015-02-03 - quick test for Robin
def confidence_interval_evaluation(df_file):
    df = read_df_from_file(df_file)
    d = []
    n = 25
    for i in range(1, n):
        interval = i / n
        add_placement_type_column(df=df, ci=interval)
        counts = df.placement_type.value_counts()
        c_count = counts.confident
        f_count = counts.fuzzy
        total_count = c_count + f_count
        d.append([interval, c_count, f_count, total_count, c_count / total_count])

    return pd.DataFrame(data=d,
                        columns=['confidence_interval', 'confident_count', 'fuzzy_count', 'total_count', 'conf/tot'])


def remove_top_right_lines_and_ticks(plot):
    plot.spines['right'].set_visible(False)
    plot.spines['top'].set_visible(False)
    plot.xaxis.set_ticks_position('bottom')
    plot.yaxis.set_ticks_position('left')


def plot_confidence_interval_evaluation(df, image_file):
    fig, ax = plt.subplots(2, sharex=True)
    top = ax[0]
    bottom = ax[1]

    p1 = top.plot(df['confidence_interval'], df['conf/tot_14'] * 100, color='y')
    p2 = top.plot(df['confidence_interval'], df['conf/tot_12'] * 100, color='b')
    top.set_ylabel(' %confident placements')
    remove_top_right_lines_and_ticks(top)
    top.legend((p1[0], p2[0]), ('2014', '2012'))

    # enough space for both bars and bar sized gap
    width = (df['confidence_interval'][1] - df['confidence_interval'][0]) / 3
    p3 = bottom.bar(df['confidence_interval'] - width, df['confident_count_14'], color='y', width=width)
    p4 = bottom.bar(df['confidence_interval'], df['confident_count_12'], color='b', width=width)
    bottom.set_ylabel('confident placements')
    remove_top_right_lines_and_ticks(bottom)
    bottom.legend((p3[0], p4[0]), ('2014', '2012'))

    plt.xlabel('confidence interval')
    fig.savefig(image_file)
    plt.close(fig)
    del fig


if __name__ == '__main__':
    df2012 = confidence_interval_evaluation(MBARI_2012_LINEAGE_FILE)
    df2014 = confidence_interval_evaluation(MBARI_2014_LINEAGE_FILE)
    # merge two data frames and save
    df = pd.merge(df2012, df2014, on='confidence_interval', how='outer', suffixes=('_12', '_14'))
    write_df_to_file(df, MBARI_ANALYSIS_DIR + 'confidence_interval_comparison.tsv')

    # df = read_df_from_file(MBARI_ANALYSIS_DIR + 'confidence_interval_comparison.tsv')
    plot_confidence_interval_evaluation(df, MBARI_ANALYSIS_DIR + 'confidence_interval_comparison.pdf')

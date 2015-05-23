import sys
import pandas as pd
import matplotlib.pyplot as plt
import os

dir = sys.argv[1]
# file = sys.argv[1]
file_list = [x for x in os.listdir(dir) if x.find('.res') != -1]
for file in file_list:
    data = pd.DataFrame.from_csv(dir + '/' + file, sep=',', header=0)
    sig_df = data[data['padj'] <= 0.05]
    sig_df.to_csv(dir.rstrip('/').rsplit('/',1)[1] + '_' + file.rsplit('.')[0] + '.meta.tsv', sep='\t')
    color_dict = {True: 'r', False: 'b'}
    marker_dict = {True: 's', False: 'o'}
    fig, ax = plt.subplots()
    y = data.log2FoldChange
    x = data.baseMean
    colors = [color_dict[(True if a <= 0.05 else False)] for a in data.padj]
    markers = [marker_dict[(True if a <= 0.05 else False)] for a in data.padj]

    for _x, _y, _c, _m in zip(x, y, colors, markers):
        ax.scatter(_x, _y, c=_c, s=50, edgecolors='none', marker=_m)
    # lo = ax.scatter(x, y, c=colors, edgecolors='none')

    counter = 0
    for color, x, y in zip(colors, x, y):
        if color == 'r':
            label = data.iloc[[counter]].index.tolist()[0]
            print label
            '''
            plt.annotate(
                label,
                xy = (x, y), xytext = (-20, 20),
                textcoords = 'offset points', ha = 'left', va = 'bottom',
                bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5),
                arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0')
            )
            '''
        counter += 1
    for label in (ax.get_xticklabels() + ax.get_yticklabels()):
        label.set_fontsize(16)
    plt.ylabel('log2FoldChange', fontsize=16)
    plt.xlabel('baseMean', fontsize=16)
    plt.title(file.split('/')[-1].split('.')[0])
    plt.savefig(dir.rstrip('/').rsplit('/',1)[1] + '_' + file.rsplit('.')[0] + '.meta.png')
    plt.clf()
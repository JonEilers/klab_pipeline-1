import os
import sys

import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np


# Global path and directory list
home_path = os.path.dirname(os.path.realpath(__file__))

# In the commandline: "python plottyPlot.py [path to files]"
# ex. commandline: "python plottyPlot.py ./rare_files/"
file_directory = sys.argv[1]
print file_directory


def main():
    rare_plot(os.walk(file_directory))
    trans_plot(os.walk(file_directory))


def rare_plot(rare_dir):
    for root, dirs, files in rare_dir:
        axis_dictionary = {}
        # library = root.split('/')[-1]
        # project = root.split('/')[-1]
        axis_dictionary['MAX_X'] = 0
        axis_dictionary['MAX_Y'] = 0
        for file in files:
            if file.find('.rare') != -1:
                x = []
                y = []
                gene = file.split('.')[0]

                input = open(root + '/' + file, 'r')
                for line in input:
                    if line.find('k') == -1:
                        split_line = line.strip('\n').split(',')
                        k = float(split_line[0])
                        r = float(split_line[1])
                        x.append(k)
                        y.append(r)
                input.close()

                if x != [] and float(max(x)) >= axis_dictionary['MAX_X']:
                    axis_dictionary['MAX_X'] = max(x)
                if y != [] and float(max(y)) >= axis_dictionary['MAX_Y']:
                    axis_dictionary['MAX_Y'] = max(y)
                axis_dictionary[gene] = x, y

        for gene, data in axis_dictionary.iteritems():
            if gene.find('MAX_') == -1:
                max_x = axis_dictionary['MAX_X']
                max_y = axis_dictionary['MAX_Y']
                x = data[0]
                y = data[1]
                line = plt.plot(x, y, '-')
                plt.setp(line, color='r', linewidth=2.0)
                if max_x != None and max_y != None:
                    if len(x) != 0 and len(y) != 0:
                        if float(x[-1]) != 0 and float(y[-1]) != 0:
                            if (float(x[-1]) / max_x) > 0.6 or (float(y[-1]) / max_y) > 0.6:
                                plt.annotate(gene, xy=(x[-1], y[-1]), xytext=(x[-1], y[-1]),
                                             bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.5))
                                # plt.annotate(gene, xy = (x[-1], y[-1]), xytext = (-(x[-1] * 0.01), y[-1] * 0.1), textcoords = 'offset points', ha = 'right', va = 'bottom',
                                #	bbox = dict(boxstyle = 'round,pad=0.5', fc = 'yellow', alpha = 0.5)), arrowprops = dict(arrowstyle = '->', connectionstyle = 'arc3,rad=0'))
        plot_title = "tester"
        plt.title(plot_title)
        plt.ylabel('r')
        plt.xlabel('k')
        plt.savefig(home_path + '/' + plot_title + '.png')
        plt.clf()
        # print project


def trans_plot(trans_dir):
    axis_dictionary = {}
    for root, dirs, files in trans_dir:
        gene = root.split('/')[-1]
        for file in files:
            if file.find('.trans') != -1:
                id = []
                x = []
                y = []
                input = open(root + '/' + file, 'r')
                for line in input:
                    split_line = line.strip('\n').split(',')
                    gene_lib_id = split_line[0]
                    pca1 = float(split_line[1])
                    pca2 = float(split_line[2])
                    id.append(gene_lib_id)
                    x.append(pca1)
                    y.append(pca2)
                input.close()
                axis_dictionary[gene] = id, x, y
    for gene, data in axis_dictionary.iteritems():
        id = data[0]
        x = data[1]
        y = data[2]
        colors = iter(cm.rainbow(np.linspace(0, 1, len(id))))
        ax = plt.subplot(111)
        for gene_lib_id in id:
            ax.scatter(x[id.index(gene_lib_id)], y[id.index(gene_lib_id)],
                       label=gene_lib_id.split('.')[1], color=next(colors))
        box = ax.get_position()
        ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        plot_title = gene
        plt.title(plot_title)
        plt.ylabel('pca2')
        plt.xlabel('pca1')
        plt.savefig(home_path + '/' + plot_title + '.png', bbox_inches='tight', dpi=100)
        plt.clf()
        print gene


if __name__ == '__main__':
    main()

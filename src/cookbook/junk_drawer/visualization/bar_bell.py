import sys

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages


# from ggplot import *


meta_file = sys.argv[1]
meta_df = pd.read_csv(meta_file, sep=',', header=0, index_col=None, lineterminator='\n')
data_file = sys.argv[2]
data_df = pd.read_csv(data_file, sep='\t', header=0, index_col=None, lineterminator='\n')

pp = PdfPages('bars.pdf')

for year in list(set(meta_df.year)):

    subset_meta = meta_df[(meta_df.year == year) & (meta_df.seq_type == 'DNA')].sort(['depth'])
    # create dataframe using trimmed up metadata
    subset_data = data_df[data_df.sra_id.isin(subset_meta.sra_id)]
    graph_list = ['domain_name', 'division_name', 'lowest_classification_name', 'functional_category']
    # iterate through the graph list to create graphs
    for graph_type in graph_list:
        # group data by each graph type to count up read hits
        graph_data = subset_data.groupby(['sra_id', graph_type])['count'].sum().reset_index()
        if graph_type == 'functional_category':
            # create a df with split up functions to count all of them
            functional_list = graph_data.functional_category.str.split(',').tolist()
            func_split_data = []
            for funcs_index in range(0, len(functional_list) - 1):
                funcs = functional_list[funcs_index]
                for function in funcs:
                    func_split_data.append(map(list, graph_data.loc[[funcs_index]].values)[0] + [function])
            func_split_col_names = list(graph_data.columns) + ['split_function']
            func_split_df = pd.DataFrame(func_split_data, columns=func_split_col_names)
            print func_split_df.head()
            # use the new split column for the graph_type and new df for graph_data
            graph_type = 'split_function'
            graph_data = func_split_df.groupby(['sra_id', graph_type])['count'].sum().reset_index()
        # remove whitespace
        graph_data[graph_type] = graph_data[graph_type].map(lambda x: x.replace(' ', '_'))
        graph_type_list = []
        # search through each bar and make a complete list of graph type names
        for sra in list(set(graph_data.sra_id)):
            sra_graph = graph_data[graph_data.sra_id.isin([sra])]
            graph_type_list = list(set(graph_type_list + list(set(sra_graph[graph_type]))))
        # add mising names to each bar data
        for sra in list(set(graph_data.sra_id)):
            sra_graph = graph_data[graph_data.sra_id.isin([sra])]
            for name in graph_type_list:
                sra_found = any(sra_graph['sra_id'] == sra)
                name_found = any(sra_graph[graph_type] == name)
                if sra_found == True and name_found == False:
                    new_value = pd.DataFrame(index=[0], columns=['sra_id', graph_type, 'count'])
                    new_value.loc[0] = pd.Series({'sra_id': sra, graph_type: name, 'count': 0})
                    graph_data = graph_data.append(new_value)

        # add depth to graph data for sorting purposes
        id2depth_df = subset_meta[['sra_id', 'depth']]
        graph_data = pd.merge(graph_data, id2depth_df, on='sra_id', how='outer')
        # sort the graph data by graph_type so that colors are the same in each bar
        graph_data = graph_data.sort([graph_type], ascending=[True])
        # try matplotlib
        patch_handles = []
        fig = plt.figure(figsize=(10, 8))
        ax = fig.add_subplot(111)

        left = np.zeros(len(graph_data.sra_id), )
        row_counts = np.zeros(len(graph_data.sra_id), )
        rows = list(graph_data['sra_id'])
        widths = list(graph_data['count'])
        labels = list(graph_data[graph_type])
        depths = list(graph_data['depth'])
        depths_sorted = sorted(list(set(depths)), reverse=True)
        print graph_data.head()
        # set color scheme
        colors = 'bgrcmykw'

        for (r, w, l, d) in zip(rows, widths, labels, depths):  # zip_up_data:
            depth_index = depths_sorted.index(d)
            patch_handles.append(ax.barh(depth_index, w, align='center', left=left[depth_index],
                                         color=colors[int(row_counts[depth_index]) % len(colors)])
                                 )
            left[depth_index] += w
            row_counts[depth_index] += 1

        y_pos = range(0, len(depths_sorted))
        ax.set_yticks(y_pos)
        ax.set_yticklabels(depths_sorted)
        ax.set_xlabel('hit_counts')
        plt.suptitle(str(year) + ' ' + graph_type)

        pp.savefig(fig)
        plt.clf()
pp.close()

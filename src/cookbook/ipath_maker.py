#!/usr/bin/env python

import os
import sys
import pandas as pd

count_file = sys.argv[1]
outfile = sys.argv[2]
data = pd.read_csv(count_file, sep='\t', index_col=False)
colors = ['#0000ff', '#00ff00']

data = data.groupby(['gene', 'sample']).sum().reset_index()
data['count'] = 'W' + data['count'].astype(str)
data['color_code'] = colors[0]
data.to_csv(outfile, sep='\t', header=False, index=False)

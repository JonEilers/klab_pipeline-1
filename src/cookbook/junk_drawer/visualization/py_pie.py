import sys

import pandas as pd
import matplotlib.pyplot as plt

file = sys.argv[1]
outfile = sys.argv[2]

data = pd.DataFrame.from_csv(file, sep=',', header=0, index_col=False)

x_list = [1, 3, 6]
label_list = ["bells", "whistles", "pasta"]

plt.axis("equal")
plt.pie(
    x_list,
    labels=label_list,
    autopct="%1.1f%%"
)
plt.title('AWPD by depth and year for COGs in ETSP OMZ')
plt.savefig(outfile)
plt.clf()

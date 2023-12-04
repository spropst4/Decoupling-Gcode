from pathlib import Path

import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import os
# load packages
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

from matplotlib.ticker import MultipleLocator,FormatStrFormatter,MaxNLocator
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.colors as mcol

# set default global settings
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'
#mpl.rcParams['figsize'] = (10,5)

SMALL_SIZE = 15 #46
MEDIUM_SIZE = 15
BIGGER_SIZE = 15

mpl.rc('font', size=SMALL_SIZE)          # controls default text sizes
mpl.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
mpl.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and abs_y labels
mpl.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
mpl.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
mpl.rc('figure', figsize = (10,5))      # figure/canvas size (inches); (width, height)

mpl.rcParams['lines.linewidth'] = 1.5 #6
mpl.rcParams['axes.linewidth'] = 1 #2     # set size of plot border
mpl.rcParams['xtick.major.pad']= '1' #'10'
mpl.rcParams['ytick.major.pad']='1'#'10'

pos_on_canvas = (0.15, 0.25, 0.5, 0.5)

path = '/GraphingGradientInfill/231031_GradientInfillWeights.txt'

upper_weight_range = 5.63
lower_weight_range = 5.48
average_weight = ((upper_weight_range+lower_weight_range)/2)

print((upper_weight_range-lower_weight_range)/average_weight)

#
upper_weight_range_large = 5.89
lower_weight_range_large = 5.45
average_weight_large = ((upper_weight_range_large+lower_weight_range_large)/2)

df = pd.read_csv(path, sep='\s+')
print(df)
weight_list = df["Weight"].values.tolist()
label_list  = df['Type'].values.tolist()
for i in range(len(weight_list)):
    if 'NG' in label_list[i]:
        color = 'red'
    else:
        color = 'c'
    plt.scatter(x = weight_list[i], y = 1, label = label_list[i], alpha = 0.5, color = color)

plt.xlabel('Sample Weights')

plt.axvspan(lower_weight_range_large, upper_weight_range_large, alpha=0.15, color='black')
#plt.axvline(average_weight_large, linestyle= 'dashed', color = 'gray')

plt.axvspan(lower_weight_range, upper_weight_range, alpha=0.15, color='navy', linestyle = 'dashed')
#plt.axvline(average_weight, linestyle= 'dashed', color = 'gray')
plt.tick_params(labelleft=False, left=False)


plt.show()

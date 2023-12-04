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
mpl.rcParams['pdf.fonttype'] = 42 #these are good font settings for adobe illustrator
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'
#mpl.rcParams['figsize'] = (10,5)


'''Define font size using pt (e.g., 8 pt, 10 pt, etc)'''
SMALL_SIZE = 20 #46
MEDIUM_SIZE = 20
BIGGER_SIZE = 20

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

## Folder path for all data - make sure you use \\ instead of \
path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\Samples_without_Plates\\"
density_path = 'DiamondLattice_Density_V2.txt'

pp = PdfPages('Diamond_DensityPlot_V2data_lowdensity.pdf')#PdfPages('231023_GradientInfill_Compression_WeightRange2.pdf')
df = pd.read_csv(density_path, sep='\s+')
relative_density_list = df["RelativeDensity"].values.tolist()
type_list = df["Type"].values.tolist()
allowed_Reldensity_range = [0, 0.280593479]# densities in this range will be plotted and used as part of the averages.
# v2 = [0.276882568,0.313194903]
# v2 low density = [0, 0.280593479]

GRAD_relative_density_list = []
NoGRAD_relative_density_list = []
for i in range(len(relative_density_list)):
    if allowed_Reldensity_range[0] < relative_density_list[i] < allowed_Reldensity_range[1]:
        if type_list[i] == 'G':
            GRAD_relative_density_list.append(relative_density_list[i])
        elif type_list[i] == 'NG':
            NoGRAD_relative_density_list.append(relative_density_list[i])

print(GRAD_relative_density_list)
print(NoGRAD_relative_density_list)
average_G_rd = np.average(GRAD_relative_density_list)
average_NG_rd = np.average(NoGRAD_relative_density_list)
std_G_rd = np.std(GRAD_relative_density_list)
std_NG_rd = np.std(NoGRAD_relative_density_list)

print(average_G_rd, average_NG_rd)
print(std_G_rd, std_NG_rd)
print(std_G_rd/average_G_rd, std_NG_rd/average_NG_rd)

fig1 = plt.figure()

for i in range(len(GRAD_relative_density_list)):
    plt.scatter(x = GRAD_relative_density_list[i], y = 1, color = 'c')
for i in range(len(NoGRAD_relative_density_list)):
    plt.scatter(x=NoGRAD_relative_density_list[i], y=1, color='r')


pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

plt.bar(x = ['Gradient', 'No Gradient'],height = [average_G_rd,average_NG_rd ], color = ['c', 'r'], alpha = 0.5)
plt.errorbar(yerr = std_G_rd, x = 'Gradient', y = average_G_rd, color = 'k')
plt.errorbar(yerr = std_NG_rd, x = 'No Gradient', y = average_NG_rd, color = 'k')
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

plt.show()

pp.close() # closes pdf file
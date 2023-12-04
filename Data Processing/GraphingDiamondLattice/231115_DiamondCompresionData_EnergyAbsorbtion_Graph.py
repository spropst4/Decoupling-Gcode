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

pp = PdfPages('Diamond_energy_absorb_V2data.pdf')#PdfPages('231023_GradientInfill_Compression_WeightRange2.pdf')
df = pd.read_csv(density_path, sep='\s+')
relative_density_list = df["RelativeDensity"].values.tolist()
L_list = df["L"].values.tolist() # Length for strain
A_list = df["A"].values.tolist() # Cross-sectional Area for stress

allowed_Reldensity_range = [0.276882568, 0.313194903] # densities in this range will be plotted and used as part of the averages.
# v2 = [0.276882568,0.313194903]
avg_densification = 0.699320675

f_list = os.listdir(path)

print(f_list)
gradient_stress_list = []
gradient_strain_list = []
NOgradient_stress_list = []
NOgradient_strain_list = []
all_plots_strain_list = []
all_plots_stress_list = []
Gradient_energy_absorption_list = []
NoGradient_energy_absorption_list = []
Gradient_rel_density_list = []
NoGradient_rel_density_list = []


file_count = 0
for file in f_list:
    #headers = ['mm', 'N', 'sec']
    df = pd.read_csv(path+file+"\\DAQ- Crosshead, … - (Timed).txt", sep='\s+', header = 5)
    headers = list(df.columns.values)

    relative_density = relative_density_list[file_count]
    densification = 1 - relative_density
    Length = L_list[file_count]
    Area = A_list[file_count]
    file_count += 1

    mm_list = df["mm"].values.tolist()
    n_list  = df['N'].values.tolist()

    '''Shifts/aligns all the data to zero'''
    strain_list = []
    stress_list = []
    first_val = False
    for n in range(len(n_list)):
        if n_list[n] > 1.5 or first_val == True:
            if first_val == False:
                mm_list_zero = mm_list[n]
                first_val = True


            strain = (mm_list[n]- mm_list_zero)/Length
            stress = n_list[n]/Area


            #if round(strain,1) <= 0.7:
            strain_list.append(strain)
            stress_list.append(stress)

    energy_absorption = np.trapz(stress_list, dx=1)
    #if allowed_Reldensity_range[0] < relative_density < allowed_Reldensity_range[1]:
    if '_G' in file: # for gradient files
        Gradient_energy_absorption_list.append(energy_absorption)
        Gradient_rel_density_list.append(relative_density)
    else:
        NoGradient_energy_absorption_list.append(energy_absorption)
        NoGradient_rel_density_list.append(relative_density)


'''Graph average and std'''
gradient_color = 'c'
NG_color = 'r'#'#BF4700' #'#BF008C'

Gradient_dict = {}
for i in range(len(Gradient_rel_density_list)):
    key = Gradient_energy_absorption_list[i]
    val = Gradient_rel_density_list[i]
    Gradient_dict[key] = val

NoGradient_dict = {}
for i in range(len(NoGradient_rel_density_list)):
    key = NoGradient_energy_absorption_list[i]
    val = NoGradient_rel_density_list[i]
    NoGradient_dict[key] = val

Gradient_dict = {key: value for key, value in sorted(Gradient_dict.items(), key=lambda item: item[1])}
NoGradient_dict = {key: value for key, value in sorted(NoGradient_dict.items(), key=lambda item: item[1])}

Gradient_energy_absorption_list = list(Gradient_dict.keys())
Gradient_rel_density_list = list(Gradient_dict.values())
NoGradient_energy_absorption_list = list(NoGradient_dict.keys())
NoGradient_rel_density_list = list(NoGradient_dict.values())
fig1 = plt.figure()
plt.plot(Gradient_rel_density_list, Gradient_energy_absorption_list, color = gradient_color, label = 'Gradient', marker = 'o', markersize = 10)
plt.plot(NoGradient_rel_density_list, NoGradient_energy_absorption_list, color = NG_color, label = 'No Gradient', marker = 's',markersize = 10)


# plt.xlim(0,)
# plt.ylim(0,)
plt.xlabel('Relative Density')
plt.ylabel('Energy Absorption (MPa)')
plt.legend(frameon = False, loc = 'upper left')
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

# plt.xlim(0, 10)
plt.ylim(0, )
# plt.legend(frameon = False, loc = 'lower right')
# pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background
plt.show()
pp.close() # closes pdf file
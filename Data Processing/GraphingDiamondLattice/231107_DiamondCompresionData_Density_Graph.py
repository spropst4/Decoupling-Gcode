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

pp = PdfPages('TEMP')#PdfPages('231023_GradientInfill_Compression_WeightRange2.pdf')
df = pd.read_csv(density_path, sep='\s+')
density_list = df["Density"].values.tolist()
relative_density_list = df["Relativedensity"].values.tolist()
allowed_density_range = [0,1]#[0.000271412, 0.00032351] # densities in this range will be plotted and used as part of the averages.

Length = 30 # sample height
Area = 10*30 # cross-section
f_list = os.listdir(path)

print(f_list)
gradient_n_list = []
gradient_mm_list = []
NOgradient_n_list = []
NOgradient_mm_list = []
all_plots_mm_list = []
all_plots_n_list = []
file_count = 0
for file in f_list:
    #headers = ['mm', 'N', 'sec']
    df = pd.read_csv(path+file+"\\DAQ- Crosshead, … - (Timed).txt", sep='\s+', header = 5)
    headers = list(df.columns.values)

    density = density_list[file_count]
    relative_density = relative_density_list[file_count]
    file_count += 1

    mm_list = df["mm"].values.tolist()
    n_list  = df['N'].values.tolist()

    '''Shifts/aligns all the data to zero'''
    mm_list_shift = []
    n_list_shift = []
    first_val = False
    for n in range(len(n_list)):
        if n_list[n] > 1.5 or first_val == True:
            if first_val == False:
                mm_list_zero = mm_list[n]/Length
                first_val = True

            mm_list_shift.append((mm_list[n]/Length) - mm_list_zero)
            n_list_shift.append((n_list[n]/Area)*(1/relative_density))

    if allowed_density_range[0] < density < allowed_density_range[1]:
        print(file)
        all_plots_mm_list.append(mm_list_shift)
        all_plots_n_list.append(n_list_shift)

    #plt.plot(mm_list_shift, n_list_shift, label=file)

        '''Distinguish between gradient vs no gradient '''
        if '_G' in file: # for gradient files
            gradient_n_list.append(n_list_shift)
            gradient_mm_list.append(mm_list_shift)
            #plt.plot(mm_list_shift, n_list_shift, label=str(density), linestyle = 'dashed')
        else: # for no gradient files
            NOgradient_n_list.append(n_list_shift)
            NOgradient_mm_list.append(mm_list_shift)
            plt.plot(mm_list_shift, n_list_shift, label=str(file))

        plt.legend()
plt.show()

'''Make sure all data sets are of equal length'''
def find_max_list_and_extend_n(list_of_lists):
    list_len = [len(i) for i in list_of_lists] # finds number of data points for each set
    max_len = max(list_len) # finds which data set has the maximum number of data points

    for elem in list_of_lists: # appends zeros to end of data sets that are too short/failed earlier
        elem.extend([0 for i in range(max_len - len(elem))])
def find_max_list_and_extend_mm(list_of_lists):
    list_len = [len(i) for i in list_of_lists]
    max_len = max(list_len)
    max_list_index = list_len.index(max_len) # finds which data set has the maximum number of data points

    for elem in list_of_lists: # makes sure all data sets are equal in length
        if elem != list_of_lists[max_list_index]:
            end_of_max_list = list_of_lists[max_list_index][-(max_len-len(elem)):]
            elem.extend(end_of_max_list)

find_max_list_and_extend_n(gradient_n_list)
find_max_list_and_extend_mm(gradient_mm_list)
find_max_list_and_extend_n(NOgradient_n_list)
find_max_list_and_extend_mm(NOgradient_mm_list)


'''Find moving average/std'''
def find_average_curve(list_of_lists): # calculates moving average
   return [float(sum(col)) / len(col) for col in zip(*list_of_lists)]
def find_std_error(list_of_lists): # calculates moving std
    std = [float(np.std(col)) for col in zip(*list_of_lists)]
    upperbound = [float(np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    lowerbound = [float(-np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    return std, upperbound, lowerbound

gradient_avg_n = find_average_curve(gradient_n_list)
gradient_avg_mm = find_average_curve(gradient_mm_list)
gradient_std_n_large = find_std_error(gradient_n_list)[1]
gradient_std_n_small = find_std_error(gradient_n_list)[2]
print('Average G STD = ', np.average(find_std_error(gradient_n_list)[0]))


NOgradient_avg_n = find_average_curve(NOgradient_n_list)
NOgradient_avg_mm = find_average_curve(NOgradient_mm_list)
NOgradient_std_n_large = find_std_error(NOgradient_n_list)[1]
NOgradient_std_n_small = find_std_error(NOgradient_n_list)[2]
print('Average NG STD = ', np.average(find_std_error(NOgradient_n_list)[0]))

'''Graph average and std'''
gradient_color = 'c'
NG_color = 'r'#'#BF4700' #'#BF008C'

fig1 = plt.figure()
plt.plot(NOgradient_avg_mm, NOgradient_avg_n, color = NG_color, label = 'No Gradient') # plots average as a line
plt.fill_between(NOgradient_avg_mm, NOgradient_std_n_small, NOgradient_std_n_large, alpha = 0.15, color =NG_color) # plots std as an shaded area

plt.plot(gradient_avg_mm, gradient_avg_n, color = 'c', label = 'Gradient')
plt.fill_between(gradient_avg_mm, gradient_std_n_small, gradient_std_n_large, alpha = 0.15, color =gradient_color)

plt.xlim(0,)
plt.ylim(0,)
plt.xlabel('Strain (mm/mm)')
plt.ylabel('Stress (N/mm/mm)')
plt.legend(frameon = False, loc = 'upper left')
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

plt.xlim(0, 10)
plt.ylim(0, )
plt.legend(frameon = False, loc = 'lower right')
pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

pp.close() # closes pdf file
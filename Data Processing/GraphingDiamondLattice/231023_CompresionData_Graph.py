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

#path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\Samples_with_Plates\\"
#path = 'C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\GradientInfill\\CubeGradient\Compression_Tests\\Raw_data\\'
#path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\Samples_without_Plates\\"
path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\WeightRange_2.5g\\"
#path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\WeightRange_6percentAverage_set1\\"
#path = "C:\\Users\\sprop\\OneDrive - Johns Hopkins\\Sarah Propst\\Research\\Decouple G-code\\Gradients\\WidthGradient\\DiamondLattices\\Compression Tests\\Raw Data\\WeightRange_6percentAverage_set2\\"
weight_path = '/GraphingDiamondLattice/DiamondLattice_AllWeights.txt'

pp = PdfPages('TEMP.pdf')#PdfPages('231023_GradientInfill_Compression_WeightRange2.pdf')
df = pd.read_csv(weight_path, sep='\s+')
weight_list = df["Weight"].values.tolist()
label_list  = df['Type'].values.tolist()
print(label_list)

f_list = os.listdir(path)
#f_list = f_list[1:]
# print(f_list)
# f_list = [f_list[0],
#           f_list[1],
#           #f_list[2],
#           f_list[3],
#           #f_list[4],
#           f_list[5]
#           ]

# f_list = ['Test Run 13 231023_CompressionData_231005_G_4','Test Run 6 231023_CompressionData_231010_G_3','Test Run 9 231023_CompressionData_231010_NG_5','Test Run 8 231023_CompressionData_231010_G_4','Test Run 10 231023_CompressionData_231010_G_5','Test Run 14 231023_CompressionData_231005_NG_1']

print(f_list)
gradient_n_list = []
gradient_mm_list = []
NOgradient_n_list = []
NOgradient_mm_list = []
for file in f_list:
    #headers = ['mm', 'N', 'sec']
    df = pd.read_csv(path+file+"\\DAQ- Crosshead, … - (Timed).txt", sep='\s+', header = 5)
    headers = list(df.columns.values)

    # for i in range(len(2)):
    #     x = list(data.iloc[:, i].values)

    mm_list = df["mm"].values.tolist()
    n_list  = df['N'].values.tolist()

    mm_list_shift = []
    n_list_shift = []
    first_val = False
    for n in range(len(n_list)):
        if n_list[n] > 1.5 or first_val == True:
            if first_val == False:
                mm_list_zero = mm_list[n]
                first_val = True

            mm_list_shift.append(mm_list[n] - mm_list_zero)
            n_list_shift.append(n_list[n])

    for i in range(len(label_list)):
        if label_list[i] in file:
            print(True)
            label = label_list[i] + " " + str(weight_list[i]) + "g"
        # else:
        #     label = file

    plt.legend()
    if '_G' in file:
        gradient_n_list.append(n_list_shift)
        gradient_mm_list.append(mm_list_shift)
        plt.plot(mm_list_shift, n_list_shift, label=label, linestyle = 'dashed')
    else:
        #graph = plt.plot(mm_list_shift, n_list_shift, label=file)
        NOgradient_n_list.append(n_list_shift)
        NOgradient_mm_list.append(mm_list_shift)
        plt.plot(mm_list_shift, n_list_shift, label=label)



    #graph = plt.plot(mm_list, n_list, label = file)
#define the function#
def find_max_list_and_extend_n(list_of_lists):
    list_len = [len(i) for i in list_of_lists]
    max_len = max(list_len)

    for elem in list_of_lists:
        elem.extend([0 for i in range(max_len - len(elem))])
def find_max_list_and_extend_mm(list_of_lists):
    list_len = [len(i) for i in list_of_lists]
    max_len = max(list_len)
    max_list_index = list_len.index(max_len)


    for elem in list_of_lists:
        if elem != list_of_lists[max_list_index]:
            end_of_max_list = list_of_lists[max_list_index][-(max_len-len(elem)):]
            elem.extend(end_of_max_list)

find_max_list_and_extend_n(gradient_n_list)
find_max_list_and_extend_mm(gradient_mm_list)
find_max_list_and_extend_n(NOgradient_n_list)
find_max_list_and_extend_mm(NOgradient_mm_list)

def find_average_curve(list_of_lists):
   return [float(sum(col)) / len(col) for col in zip(*list_of_lists)]
def find_std_error(list_of_lists):
    std = [float(np.std(col)) for col in zip(*list_of_lists)]
    upperbound = [float(np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    lowerbound = [float(-np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    return std, upperbound, lowerbound

gradient_avg_n = find_average_curve(gradient_n_list)
gradient_avg_mm = find_average_curve(gradient_mm_list)
gradient_std_n_large = find_std_error(gradient_n_list)[1]
gradient_std_n_small = find_std_error(gradient_n_list)[2]

NOgradient_avg_n = find_average_curve(NOgradient_n_list)
NOgradient_avg_mm = find_average_curve(NOgradient_mm_list)
NOgradient_std_n_large = find_std_error(NOgradient_n_list)[1]
NOgradient_std_n_small = find_std_error(NOgradient_n_list)[2]

# NOgradient_avg_n.append(0)
# NOgradient_avg_mm.append(NOgradient_avg_mm[-1])
# NOgradient_std_n_large.append(0)
# NOgradient_std_n_small.append(0)

gradient_color = 'c'
NG_color = 'r'#'#BF4700' #'#BF008C'

fig1 = plt.figure()
plt.plot(NOgradient_avg_mm, NOgradient_avg_n, color = NG_color, label = 'No Gradient')
plt.fill_between(NOgradient_avg_mm, NOgradient_std_n_small, NOgradient_std_n_large, alpha = 0.15, color =NG_color)

plt.plot(gradient_avg_mm, gradient_avg_n, color = 'c', label = 'Gradient')
plt.fill_between(gradient_avg_mm, gradient_std_n_small, gradient_std_n_large, alpha = 0.15, color =gradient_color)

plt.xlim(0,)
plt.ylim(0,)
plt.xlabel('Compression (mm)')
plt.ylabel('Force (N)')
plt.legend(frameon = False, loc = 'upper left')
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True)

plt.xlim(0, 10)
plt.ylim(0, 600)
plt.legend(frameon = False, loc = 'lower right')
pp.savefig(fig1, transparent = True)

plt.show()

pp.close()


#print(mm_list)



# See PyCharm help at https://www.jetbrains.com/help/pycharm/

'''
Author: Sarah Propst
Date: 12/3/2023

Purpose: This code graphs data created by Measure_each_color.py
'''


import cv2 # if there is an error try importing as OpenCV
import csv
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
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
SMALL_SIZE = 8 #46
MEDIUM_SIZE = 8
BIGGER_SIZE = 8

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

'''Export Paths'''
pp = PdfPages('IndexedCoextrude_03/Graphs_IndexedCoextrude_03_V1.pdf')

'''Data Path'''
pressure_path = 'IndexedCoextrude_03/IndexedCoextrude_03_Pressures.txt'
Measure_color_results_path = 'IndexedCoextrude_03/Results_IndexedCoextrude_03.csv'

'''Extract Data'''
### Pressures
df = pd.read_csv(pressure_path, sep='\s+')
color1_pressure_list = df["Red"].values.tolist()
color2_pressure_list = df["Blue"].values.tolist()
pressure_ratio_1to2_list = []
pressure_diff_list = []
for i in range(len(color1_pressure_list)):
    pressure_ratio_1to2 = color1_pressure_list[i] / color2_pressure_list[i]
    pressure_ratio_1to2_list.append(pressure_ratio_1to2)

    pressure_diff = abs(color1_pressure_list[i]-color2_pressure_list[i])
    pressure_diff_list.append(pressure_diff)

### Width Results
df = pd.read_csv(Measure_color_results_path, sep=',')
col_labels = ['color1_avg_width_list', 'color2_avg_width_list', 'color1_std_list', 'color2_std_list', 'total_width_list']
color1_avg_width_list = df[col_labels[0]]
color2_avg_width_list = df[col_labels[1]]
color1_std_list = df[col_labels[2]]
color2_std_list = df[col_labels[3]]
total_width_list = df[col_labels[4]]


#Plot against color1 pressure
x = color1_pressure_list
fig1 = plt.figure()
plt.errorbar(yerr = color1_std_list, x = x, y = color1_avg_width_list, markersize = 4, marker = 'o', color = 'r', ecolor ='k', capsize =0.75, label = 'Red')
plt.errorbar(yerr = color2_std_list, x = x, y = color2_avg_width_list, markersize = 4, marker = 's', color = 'c', ecolor ='k', capsize =0.75, label = 'Blue')

plt.plot(x, total_width_list, marker ='^', color ='purple', label = 'Total')

plt.xlabel('Red Pressure (psi)')
plt.ylabel('Width (mm)')
plt.legend()
plt.tick_params(direction = "in")

#pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background

#Plot against color1 - color2 (pressure_diff_list)
x = pressure_diff_list
fig2 = plt.figure()
plt.errorbar(yerr = color1_std_list, x = x, y = color1_avg_width_list, markersize = 4, marker = 'o', color = 'r', ecolor ='k', capsize =0.75, label = 'Red')
plt.errorbar(yerr = color2_std_list, x = x, y = color2_avg_width_list, markersize = 4, marker = 's', color = 'c', ecolor ='k', capsize =0.75, label = 'Blue')

plt.plot(x, total_width_list, marker ='^', color ='purple', label = 'Total')

plt.xlabel('Pressure difference (Red - Blue) (psi)')
plt.ylabel('Width (mm)')
plt.legend()
plt.tick_params(direction = "in")
# pp.savefig(fig2, transparent = True) # writes graph to pdf with transparent background


#Plot against ratio between color1/color2 = r/b
x = pressure_ratio_1to2_list
fig3 = plt.figure()
plt.errorbar(yerr = color1_std_list, x = x, y = color1_avg_width_list, markersize = 4, marker = 'o', color = 'r', ecolor ='k', capsize =0.75, label = 'Red')
plt.errorbar(yerr = color2_std_list, x = x, y = color2_avg_width_list, markersize = 4, marker = 's', color = 'c', ecolor ='k', capsize =0.75, label = 'Blue')

plt.plot(x, total_width_list, marker ='^', color ='purple', label = 'Total')

plt.xlabel('Pressure ratio (Red/Blue)')
plt.ylabel('Width (mm)')
plt.legend()
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True) # writes graph to pdf with transparent background
pp.savefig(fig2, transparent = True) # writes graph to pdf with transparent background
pp.savefig(fig3, transparent = True) # writes graph to pdf with transparent background
pp.close()
plt.show()
'''
Good tutorials:
https://towardsdatascience.com/making-publication-quality-figures-in-python-part-ii-line-plot-legends-colors-4430a5891706

'''
import numpy as np
# load packages
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter,MaxNLocator
from itertools import cycle, islice
import matplotlib.cm as cm

# set default global settings
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

mpl.rc('font', size=SMALL_SIZE)          # controls default text sizes
mpl.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
mpl.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
mpl.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
mpl.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# import data
import pandas as pd
data = pd.read_csv("effect_of_numCommands_varyFeed_V3.csv", header = 0)
data2 = pd.read_csv("effect_of_numCommands_varyAccel_V3.csv", header = 0)
headers = list(data.columns.values)
# print(headers)
# print(data.to_string())

y = []
y2 = []
for i in range(len(headers)):

    if i == 0:
        x = list(data.iloc[:,i].values)
        x2 = list(data2.iloc[:, i].values)
    else:
        y.append(list(data.iloc[:, i].values))
        y2.append(list(data2.iloc[:, i].values))


y_v25 = y[0]
time_based_y_v25 = y[0][0]

y_v20 = y[1]
time_based_y_v20 = y[1][0]

# set figure-specifics parameters
fig1 = plt.figure(figsize = (5, 5))             # figure size **plt.figure() keeps default
ax1 = plt.axes((0.2, 0.1, 0.5, 0.8))              # position on canvas (left, bottom, width, height) - canvas in range (0,1)


colors = cm.inferno_r(np.linspace(0.3, 1, len(headers)-1))

trad_v20 = ax1.plot(x, y_v20,
                    color= colors[1],
                    linestyle='-',
                    linewidth= 1.5,

                    label = 'traditional')

time_v20 = ax1.axhline(y = time_based_y_v20,
                       color=colors[1],

                       linestyle = '--',
                       linewidth = 1.5,

                       label = 'time-based')

ax1.legend(handles = [trad_v20[0], time_v20],
           labels = ['traditional', 'time-based'],
           frameon = False,
           loc = 'center right'
           )

plt.xlim([0, max(x)])
plt.ylim([0, max(y_v20) + 2])

plt.xlabel("Number of actions per 100 mm")
plt.ylabel("Total print time (s)")

ax1.tick_params(axis ='x', direction ='in')
ax1.tick_params(axis ='y', direction ='in')

ax1.xaxis.set_major_locator(MultipleLocator(max(x)/4))
ax1.yaxis.set_major_locator(MultipleLocator(max(y_v20) / 4))

### Vary Feed

fig2 = plt.figure(figsize = (5, 5))             # figure size **plt.figure() keeps default
ax2 = fig2.add_axes((0.2, 0.1, 0.5, 0.8))              # position on canvas (left, bottom, width, height) - canvas in range (0,1)

# colors = plt.cm.rainbow(np.linspace(0, 1,len(headers)-1))
colors = cm.inferno_r(np.linspace(0.3, 1, len(headers)-1))

for i in range(len(headers)-1):
    ax2.plot(x, y[i], color = colors[i])
    ax2.axhline(y=y[i][0], color = colors[i], linestyle ="--")


plt.xlim([0, max(x)])
plt.ylim([0, np.max(y) + 2])

plt.xlabel("Number of actions per 100 mm")
plt.ylabel("Total print time (s)")

ax2.tick_params(axis ='x', direction ='in')
ax2.tick_params(axis ='y', direction ='in')

ax2.xaxis.set_major_locator(MultipleLocator(max(x)/4))
ax2.yaxis.set_major_locator(MultipleLocator(np.max(y) / 4))

### Vary Accel

fig3 = plt.figure(figsize = (5, 5))             # figure size **plt.figure() keeps default
ax3 = fig3.add_axes((0.2, 0.1, 0.5, 0.8))              # position on canvas (left, bottom, width, height) - canvas in range (0,1)

# colors = plt.cm.rainbow(np.linspace(0, 1,len(headers)-1))
colors = cm.inferno_r(np.linspace(0.3, 1, len(headers)-1))

for i in range(len(headers)-1):
    ax3.plot(x2, y2[i], color = colors[i])
    ax3.axhline(y=y2[i][0], color = colors[i], linestyle ="--")


plt.xlim([0, max(x2)])
plt.ylim([0, np.max(y2) + 2])

plt.xlabel("Number of actions per 100 mm")
plt.ylabel("Total print time (s)")

ax3.tick_params(axis ='x', direction ='in')
ax3.tick_params(axis ='y', direction ='in')

ax3.xaxis.set_major_locator(MultipleLocator(max(x2)/4))
ax3.yaxis.set_major_locator(MultipleLocator(np.max(y2) / 4))

plt.show()

plt.show()

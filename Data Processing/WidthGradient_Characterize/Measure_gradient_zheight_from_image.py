
import cv2
from scipy.interpolate import make_interp_spline
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

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
mpl.rc('figure', figsize = (5,2))      # figure/canvas size (inches); (width, height)

mpl.rcParams['lines.linewidth'] = 1#6
mpl.rcParams['axes.linewidth'] = 0.75#2     # set size of plot border
mpl.rcParams['xtick.major.pad']= '1' #'10'
mpl.rcParams['ytick.major.pad']='1'#'10'

pos_on_canvas = (0.15, 0.25, 0.5, 0.5)

###############################################################################################################
def scale_bar_process_image(scale_bar_image, scale_length_mm):
    img = cv2.imread(scale_bar_image, 0)
    scale_length_pix = img.shape[0]
    scale_factor = scale_length_mm/scale_length_pix
    return scale_factor

def process_image(image, scale_factor):
    black = 30 # upper range
    white = 255  # upper range

    num_filament_pix_list = []
    x_dist = []
    img = cv2.imread(image, 0)

    for row in range(len(img)):

        num_pix_total = len(img[row])

        num_black_pix = np.sum(img[row] <= black)
        num_filament_pix = num_pix_total - (num_black_pix)

        num_filament_pix_list.append(num_filament_pix * scale_factor)

        x_dist.append(row*scale_factor)

    return x_dist, num_filament_pix_list

pp = PdfPages('230706_zheight_15to65psi_1incr_and_10incr_for_230817_8ptFont.pdf')

scale_bar_image = '230706_1mm50pixels_ScaleBar_230731_ruler_edge.png'
scale_length_mm = 1
scale_factor = scale_bar_process_image(scale_bar_image, scale_length_mm)

fig1 = plt.figure()
image = '230706_Photo_zheight_230731_15to65psi_10incr_for_python_Traditional.png'
output = process_image(image, scale_factor)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, color = 'k')

image = '230706_Photo_zheight_230731_15to65psi_10incr_for_python_DGC.png'
output = process_image(image, scale_factor)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width)
plt.xlim(0, 40)
plt.ylim(0, 3)

plt.xlabel('Distance (mm)')
plt.ylabel('Filament height (mm)')

plt.legend(labels = ['Conventional', 'Time-based'],
           frameon = False
           )
plt.tick_params(direction = "in")

########################################
fig2 = plt.figure()
image = '230706_Photo_zheight_230731_15to65psi_1incr_for_python_v2_Traditional.png'
output = process_image(image, scale_factor)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, color = 'k')

#fig3 = plt.figure()
image = '230706_Photo_zheight_230731_15to65psi_1incr_for_python_v2_DGC.png'
output = process_image(image, scale_factor)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width)

plt.xlim(0, 40)
plt.ylim(0, 3)

plt.xlabel('Distance (mm)')
plt.ylabel('Filament height (mm)')

plt.legend(labels = ['Conventional', 'Time-based'],
           frameon = False
           )
plt.tick_params(direction = "in")

pp.savefig(fig1, transparent = True)
pp.savefig(fig2, transparent = True)
pp.close()

plt.show()
import numpy as np
import cv2
from scipy.interpolate import make_interp_spline
from scipy.interpolate import interp1d
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter

# load packages
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
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

SMALL_SIZE = 45
MEDIUM_SIZE = 45
BIGGER_SIZE = 45

mpl.rc('font', size=SMALL_SIZE)          # controls default text sizes
mpl.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
mpl.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
mpl.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
mpl.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title
mpl.rc('figure', figsize = (30,10))      # figure/canvas size (inches)

mpl.rcParams['lines.linewidth'] = 6
mpl.rcParams['axes.linewidth'] = 2     # set size of plot border
mpl.rcParams['xtick.major.pad']='10'
mpl.rcParams['ytick.major.pad']='10'


###############################################################################################################
def process_image_and_plot(current_img, scale):
    black = 30  # upper range
    white = 200  # upper range\
    blue = 114

    num_pix_col_1 = {}
    num_pix_col_2 = {}
    num_pix_col_3 = {}

    for i in range(len(current_img)):
        num_pix_total = len(current_img[i])
        num_white_pix_scalebar = np.sum(current_img[i] == 255)
        current_row = current_img[i]

        for j in range(len(current_row)):
            num_white_pix = np.sum(current_img[i] >= blue)
            num_blue_pix = np.sum(black < current_img[i] <= blue)

    for i in range(len(num_white_pix_scalebar_dict)):
        current_img = num_white_pix_scalebar_dict[i]
        width_values = list(current_img.values())
        scale_bar_width = np.average(width_values)
        scale_bar_std = np.std(width_values)
        scale_bar_average_dict[i] = scale_bar_width
        scale_bar_std_dict[i] = scale_bar_std
        scaled_dict[i] = scale / scale_bar_width


image_name = "230515_SCAN_4800dpi_3x7_Resync_Python_GrayScale.png"
img = cv2.imread(image_name, 0)


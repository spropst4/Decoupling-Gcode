
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
mpl.rc('figure', figsize = (2.5,1.2))      # figure/canvas size (inches); (width, height

mpl.rcParams['lines.linewidth'] = 1#6
mpl.rcParams['axes.linewidth'] = 0.75#2     # set size of plot border
mpl.rcParams['xtick.major.pad']= '1' #'10'
mpl.rcParams['ytick.major.pad']='1'#'10'

pos_on_canvas = (0.15, 0.25, 0.8, 0.5)

###############################################################################################################
def scale_bar_process_image(scale_bar_image, scale_length_mm):
    img = cv2.imread(scale_bar_image, 0)
    scale_length_pix = img.shape[0]
    scale_factor = scale_length_mm/scale_length_pix
    return scale_factor

def process_image(image, scale_factor, ideal_width):
    black = 0 # upper range
    white = 255  # upper range

    num_white_pix_list = []
    num_black_pix_list = []
    x_dist = []
    img = cv2.imread(image, 0)
    row_delete =0

    #row = int(0.5/scale_factor)
    for row in range(len(img)):
    #while row <= len(img) - 1:

        num_pix_total = len(img[row])

        num_black_pix = np.sum(img[row] == black)
        num_white_pix = num_pix_total - (num_black_pix)

        if num_white_pix > 0:
            num_white_pix_list.append(ideal_width -  num_white_pix * scale_factor)
            num_black_pix_list.append(ideal_width - num_black_pix*scale_factor)
            x_dist.append((row - row_delete)*scale_factor)

        else:
            row_delete = row + 1
        #row += int(1/scale_factor)

    return x_dist, num_white_pix_list

scale_bar_image = 'ScaleBar_10mm_3200dpi_scan.png'
scale_length_mm = 10
scale_factor = scale_bar_process_image(scale_bar_image, scale_length_mm)

ideal_width = 15

fig1 = plt.figure()

image = '230719_3200dpi_noresync_F15_indexed_diffusion0%_V2.png'
output = process_image(image, scale_factor, ideal_width)
x_dist = output[0]
fil_width = output[1]
plt.bar(x_dist, fil_width, color = 'gray')


image = '230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
output = process_image(image, scale_factor, ideal_width)
x_dist = output[0]
fil_width = output[1]
plt.bar(x_dist, fil_width)

plt.xlim(0,45)



plt.show()
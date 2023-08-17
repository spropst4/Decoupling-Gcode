'''
Sarah Propst
Updated: 230817

This code processes and graphs images of resync samples (black and white, 2 columns of 15 mm).
Uses cv2 package to count number of white and black pixels in each row.
Exports graphs in a pdf file.

'''


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
mpl.rc('figure', figsize = (5,3))      # figure/canvas size (inches); (width, height

mpl.rcParams['lines.linewidth'] = 3 #6
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

def process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal, length_y_distance_for_smoothing):
    black = 0 # upper range
    white = 255  # upper range

    num_white_pix_list = []
    num_black_pix_list = []
    x_dist = []
    img = cv2.imread(image, 0)

    #row = int(0.5/scale_factor)
    for row in range(len(img)):
    #while row <= len(img) - 1:

        num_pix_total = len(img[row])

        num_black_pix = np.sum(img[row] <= black)
        num_white_pix = num_pix_total - (num_black_pix)


        num_white_pix_list.append((num_white_pix * scale_factor))   # - (ideal_width))/ideal_width * 100)
        num_black_pix_list.append((num_black_pix*scale_factor))     # - (ideal_width))/ideal_width * 100)

        x_dist.append((row) *scale_factor)


        #row += int(1/scale_factor)



    num_rows_for_ideal = int(length_y_distance_for_ideal/scale_factor)
    average_first_n_rows_black = np.average(num_black_pix_list[0:num_rows_for_ideal])
    average_first_n_rows_white = np.average(num_white_pix_list[0:num_rows_for_ideal])

    print('average_first_n_rows_black =', average_first_n_rows_black)

    if smoothing_flag == True:

        num_rows_for_smoothing = int(length_y_distance_for_smoothing / scale_factor)
        print('num_rows_for_smoothing = ', num_rows_for_smoothing)

        i_start = 0
        i_end = i_start + num_rows_for_smoothing
        smoothed_black_pix_list = []
        smoothed_dist_list = []

        while i_end <= (len(num_black_pix_list)):
            avg_black_pix = ((np.average(num_black_pix_list[i_start: i_end]) - (average_first_n_rows_black)) / average_first_n_rows_black) * 100
            avg_distance = np.average(x_dist[i_start:i_end])
            i_start = i_end + 1
            i_end = i_start + num_rows_for_smoothing

            if absolute == True:
                avg_black_pix = (abs(avg_black_pix))

            smoothed_black_pix_list.append((avg_black_pix))
            smoothed_dist_list.append(avg_distance)

        return smoothed_dist_list, smoothed_black_pix_list

    else:
        for i in range(len(num_black_pix_list)):
            num_black_pix_list[i] = ((num_black_pix_list[i] - (average_first_n_rows_black)) / average_first_n_rows_black) * 100

            if absolute == True:
                num_black_pix_list[i] = abs(num_black_pix_list[i])

        return x_dist, num_black_pix_list


pp = PdfPages('230817_ideal3_smoothed02mm_230719_26_Scan3200dpi_Resync_F15.pdf')

scale_bar_image = 'ScaleBar_10mm_3200dpi_scan.png'
scale_length_mm = 10
scale_factor = scale_bar_process_image(scale_bar_image, scale_length_mm)

length_y_distance_for_ideal = 3 # mm (i.e., this will average the first n pixels rows equivalent to the mm input to get the ideal value)

smoothing_flag = True # do you want to smooth the plot (i.e., take average every n distance)
length_y_distance_for_smoothing = 1 #.08 # mm

absolute = False # plot absolute deviation from ideal (shows deviation as a positive number

# Descriptiopn page
firstPage = plt.figure(figsize=(11.69,8.27))
firstPage.clf()
txt = 'Date: 230817' \
      '\nGraph font: 8 pt' \
      '\nIdeal length is average of first 3 mm of rows (~first 3 filaments)' \
      '\nSmoothing: Average every 0.2 mm (~25 pixel rows)' \


firstPage.text(0.5,0.5,txt, transform=firstPage.transFigure, size=24, ha="center")
pp.savefig()


#### 230719 Sample 1
fig1 = plt.figure()
plt.title('230719 Sample 1')

image = '230719_3200dpi_NoResync_F15_Sample1_indexed.png' #'230719_3200dpi_noresync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_noresync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,length_y_distance_for_smoothing)

x_dist_noresync = output[0]
fil_width_noresync = output[1]
plt.plot(x_dist_noresync, fil_width_noresync, color = 'gray', label = 'No Resync')
plt.fill_between(x_dist_noresync, fil_width_noresync,
                 #step="pre",
                 alpha = .8,
                 color = 'gray')


image = '230719_3200dpi_Resync_F15_Sample1_indexed.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Resync')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8)



plt.axhline(y =0, linestyle = 'dashed', label = 'Ideal', color = 'k')
plt.legend(frameon = False, loc = 'lower right')

plt.xlim(0,44)
plt.ylim(-10, 10)

plt.tick_params(direction = "in")

plt.xlabel('Distance (mm)')
plt.ylabel('Deviation from ideal (%)')

pp.savefig(fig1, transparent = True)

#### 230726 Sample 2
fig2 = plt.figure()
plt.title('230726 Sample 2')
image = '230726_Plate2_3200dpi_NoResync_F15_Sample2_indexed_crop1.png' #'230719_3200dpi_noresync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_noresync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,length_y_distance_for_smoothing)

x_dist_noresync = output[0]
fil_width_noresync = output[1]
plt.plot(x_dist_noresync, fil_width_noresync, color = 'gray', label = 'No Resync')
plt.fill_between(x_dist_noresync, fil_width_noresync,
                 #step="pre",
                 alpha = .8,
                 color = 'gray')



image = '230726_Plate2_3200dpi_Resync_F15_Sample2_indexed_crop1.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Resync')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8)


plt.axhline(y =0, linestyle = 'dashed', label = 'Ideal', color = 'k')
plt.legend(frameon = False, loc = 'lower right')

plt.xlim(0,44)
plt.ylim(-10, 10)

plt.tick_params(direction = "in")

plt.xlabel('Distance (mm)')
plt.ylabel('Deviation from ideal (%)')

pp.savefig(fig2, transparent = True)

#### 230726 Sample Aero Conventional vs Resync
fig3 = plt.figure()
plt.title('230726 Sample Aero Conventional vs Resync Sample 2')
image = '230726_Plate2_3200dpi_AeroConvetional_F15_Sample1_indexed_crop1.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Conventional',color = 'gray')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8,
                 color = 'gray')

image = '230726_Plate2_3200dpi_Resync_F15_Sample2_indexed_crop1.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Resync')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8)



plt.axhline(y =0, linestyle = 'dashed', label = 'Ideal', color = 'k')
plt.legend(frameon = False, loc = 'lower right')

plt.xlim(0,44)
plt.ylim(-10, 10)

plt.tick_params(direction = "in")

plt.xlabel('Distance (mm)')
plt.ylabel('Deviation from ideal (%)')

pp.savefig(fig3, transparent = True)






#### 230726 Sample Aero Conventional vs 230719 Resync
fig4 = plt.figure()
plt.title('230726 Sample Aero Conventional vs 230719 Resync Sample 1')
image = '230726_Plate2_3200dpi_AeroConvetional_F15_Sample1_indexed_crop1.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Conventional',color = 'gray')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8,
                 color = 'gray')

image = '230719_3200dpi_Resync_F15_Sample1_indexed.png' #'230719_3200dpi_resync_F15_indexed_diffusion0%_V2.png'
#image = '230719_3200dpi_resync_F15.png'
output = process_image(image, scale_factor, absolute, smoothing_flag, length_y_distance_for_ideal,
                       length_y_distance_for_smoothing)
x_dist = output[0]
fil_width = output[1]
plt.plot(x_dist, fil_width, label = 'Resync')
plt.fill_between(x_dist, fil_width,
                 #step="pre",
                 alpha = .8)



plt.axhline(y =0, linestyle = 'dashed', label = 'Ideal', color = 'k')
plt.legend(frameon = False, loc = 'lower right')

plt.xlim(0,44)
plt.ylim(-10, 10)

plt.tick_params(direction = "in")

plt.xlabel('Distance (mm)')
plt.ylabel('Deviation from ideal (%)')

pp.savefig(fig4, transparent = True)

pp.close()

# plt.show()
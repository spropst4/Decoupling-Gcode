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
def process_image_and_plot(img_list, number_filaments_per_image, scale, colors, smooth, linestyle):
    black = 30  # upper range
    white = 200  # upper range

    num_white_pix_scalebar_dict = {}
    num_blue_pix_filament_dict = {}
    for j in range(len(img_list)):
        pix_scalebar = {}
        num_blue_pix_filament = {}

        current_img = img_list[j]
        count = 0
        for i in range(len(current_img)):
            num_pix_total = len(current_img[i])
            num_white_pix_scalebar = np.sum(current_img[3] >= 140)

            num_white_pix = np.sum(current_img[i] >= white)
            num_black_pix = np.sum(current_img[i] <= black)
            num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)

            pix_scalebar[i] = num_white_pix_scalebar / number_filaments_per_image


            num_blue_pix_filament[i] = num_blue_pix / number_filaments_per_image

        num_white_pix_scalebar_dict[j] = pix_scalebar
        num_blue_pix_filament_dict[j] = num_blue_pix_filament

    scale_bar_average_dict = {}
    scale_bar_std_dict = {}
    scaled_dict = {}
    for i in range(len(num_white_pix_scalebar_dict)):
        current_img = num_white_pix_scalebar_dict[i]
        width_values = list(current_img.values())
        scale_bar_width = np.average(width_values)
        scale_bar_std = np.std(width_values)
        scale_bar_average_dict[i] = scale_bar_width
        scale_bar_std_dict[i] = scale_bar_std
        scaled_dict[i] = scale / scale_bar_width


    for i in range(len(num_blue_pix_filament_dict)):
        current_img = num_blue_pix_filament_dict[i]
        current_scale = scaled_dict[i]
        dist_values = list(current_img.keys())
        width_values = list(current_img.values())

        dist_values_scaled = [elem * current_scale for elem in dist_values]
        width_values_scaled = [elem * current_scale for elem in width_values]

        smoothing_spline = make_interp_spline(dist_values, width_values)
        smoothing_cubic = interp1d(dist_values, width_values, kind="cubic")

        # dist_smooth = np.linspace(min(dist_values), max(dist_values), 500) # cubic and spline
        # width_smooth = smoothing_spline(dist_smooth)
        # width_smooth = smoothing_cubic(dist_smooth)

        dist_smooth = dist_values_scaled
        width_smooth = savgol_filter(width_values_scaled, 200, 3)

        if smooth == True:
            plt.plot(dist_smooth, width_smooth, color=colors[i], linestyle = linestyle)
        else:
            plt.plot(dist_values_scaled, width_values_scaled, color=colors[i], linestyle = linestyle)
def process_image_and_plot_averages(img_list, number_filaments_per_image, scale, color, smooth):
    black = 50  # upper range
    white = 255  # upper range

    num_white_pix_scalebar_dict = {}
    num_blue_pix_filament_dict = {}
    for j in range(len(img_list)):
        pix_scalebar = {}
        num_blue_pix_filament = {}

        current_img = img_list[j]
        for i in range(len(current_img)):
            num_pix_total = len(current_img[i])
            num_white_pix_scalebar = np.sum(current_img[3] == white)

            num_white_pix = np.sum(current_img[i] >= white)
            num_black_pix = np.sum(current_img[i] <= black)
            num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)

            pix_scalebar[i] = num_white_pix_scalebar / number_filaments_per_image


            num_blue_pix_filament[i] = num_blue_pix / number_filaments_per_image

        num_white_pix_scalebar_dict[j] = pix_scalebar
        num_blue_pix_filament_dict[j] = num_blue_pix_filament

    scale_bar_average_dict = {}
    scale_bar_std_dict = {}
    scaled_dict = {}
    for i in range(len(num_white_pix_scalebar_dict)):
        current_img = num_white_pix_scalebar_dict[i]
        width_values = list(current_img.values())
        scale_bar_width = np.average(width_values)
        scale_bar_std = np.std(width_values)
        scale_bar_average_dict[i] = scale_bar_width
        scale_bar_std_dict[i] = scale_bar_std
        scaled_dict[i] = scale / scale_bar_width
    print("scaled_dict = ", scaled_dict)

    avg_list = []
    std_list = []
    upper_list = []
    lower_list = []
    for j in range(len(num_blue_pix_filament_dict[0])):
        fil_width_list = []
        for i in range(len(num_blue_pix_filament_dict)):
            fil_width = num_blue_pix_filament_dict[i][j] * scaled_dict[j]
            fil_width_list.append(fil_width)

        average = np.average(fil_width_list)
        std = np.std([fil_width_list])

        avg_list.append(average)
        std_list.append(std)
        upper_list.append(average + std)
        lower_list.append(average - std)

    x_dist = list(num_blue_pix_filament_dict[0].keys())
    x_dist_scaled = [elem * (scaled_dict[0]) for elem in x_dist]

    average_smooth = savgol_filter(avg_list, 200, 3)
    lower_smooth = savgol_filter(lower_list, 200, 3)
    upper_smooth = savgol_filter(upper_list, 200, 3)

    #fig = plt.figure()
    plt.plot(x_dist_scaled, average_smooth, color=color)
    plt.fill_between(x_dist_scaled, lower_smooth, upper_smooth, alpha=0.1, color=color)

    if smooth == True:
        plt.plot(x_dist_scaled, average_smooth, color=color)
        plt.fill_between(x_dist_scaled, lower_smooth, upper_smooth, alpha=0.1, color=color)
    else:
        plt.plot(x_dist_scaled, avg_list, color=color)
        plt.fill_between(x_dist_scaled, lower_list, upper_list, alpha=0.1, color=color)
def crop_image(img, number_filaments):
    img_height = (img.shape)[0]
    img_width = (img.shape)[1]
    x_incr = int(img_width / number_filaments)

    img_list = []
    for i in range(number_filaments):
        img_new = img[0:img_height, x_incr * i: (i + 1) * x_incr]
        img_list.append(img_new)

        cv2.imwrite('test'+str(i)+'.png', img_new)
    return img_list

scale = 2.5 # scale bar is 2.5 mm

image_1000_nodefects_all = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_no_defects.png'
image_1000_all = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_editglare.png'
image_1000_all6_nodefects = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_ColorIndexed_nodefects.png'
image_1000_all6_defects = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_ColorIndexed.png'

image_1000_all6_defects_notIndexed = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_NOT_ColorIndexed.png'

image_800_nodefects_all = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_no_defects.png'
image_800_all = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_editglares.png'
image_800_all6_nodefects = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_ColorIndexed_nodefects.png'
image_800_all6_defects = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_ColorIndexed.png'

image_600_nodefects_all = '230504_SCAN_.58mm_F20_PS1_A600_2.5scalebar_python_no_defects.png'
image_600_all = '230504_SCAN_.58mm_F20_PS1_A600_2.5scalebar_python_editglares.png'
image_600_all6_nodefects = '230504_SCAN_.58mm_F20_PS1_A600_2.5scalebar_python_ColorIndexed_nodefects.png'
image_600_all6_defects = '230504_SCAN_.58mm_F20_PS1_A600_2.5scalebar_python_ColorIndexed.png'

image_400_nodefects_all = '230504_SCAN_.58mm_F20_PS1_A400_2.5scalebar_python_no_defects.png'
image_400_all = '230504_SCAN_.58mm_F20_PS1_A400_2.5scalebar_python_editglares.png'
image_400_all6_nodefects = '230504_SCAN_.58mm_F20_PS1_A400_2.5scalebar_python_ColorIndexed_nodefects.png'
image_400_all6_defects = '230504_SCAN_.58mm_F20_PS1_A400_2.5scalebar_python_ColorIndexed.png'

image_200_nodefects_all = '230504_SCAN_.58mm_F20_PS1_A200_2.5scalebar_python_no_defects.png'
image_200_all = '230504_SCAN_.58mm_F20_PS1_A200_2.5scalebar_python_editglares.png'
image_200_all6_nodefects = '230504_SCAN_.58mm_F20_PS1_A200_2.5scalebar_python_ColorIndexed_nodefects.png'
image_200_all6_defects = '230504_SCAN_.58mm_F20_PS1_A200_2.5scalebar_python_ColorIndexed.png'


################ A = 1000 ################
img_1000_nodefects_all = cv2.imread(image_1000_nodefects_all, 0)
img_1000_nodefects_list = crop_image(img_1000_nodefects_all, 3)
img_1000_all = cv2.imread(image_1000_all, 0)
img_1000_defects_list = crop_image(img_1000_all, 3)

img_1000_nodefects_all6 = cv2.imread(image_1000_all6_nodefects, 0)
img_1000_nodefects_all6_list = crop_image(img_1000_nodefects_all6, 6)

img_1000_all6 = cv2.imread(image_1000_all6_defects, 0)
img_1000_defects_all6_list = crop_image(img_1000_all6, 6)

image_1000_all6_defects_notIndexed = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_NOT_ColorIndexed.png'
img_1000_all6_not_indexed = cv2.imread(image_1000_all6_defects_notIndexed, 0)
img_1000_defects_all6_not_indexed_list = crop_image(img_1000_all6_not_indexed, 6)

################ A = 800 ################
img_800_nodefects_all = cv2.imread(image_800_nodefects_all, 0)
img_800_nodefects_list = crop_image(img_800_nodefects_all, 3)

img_800_all = cv2.imread(image_800_all, 0)
img_800_defects_list = crop_image(img_800_all, 3)


img_800_nodefects_all6 = cv2.imread(image_800_all6_nodefects, 0)
img_800_nodefects_all6_list = crop_image(img_800_nodefects_all6, 6)

img_800_all6 = cv2.imread(image_800_all6_defects, 0)
img_800_defects_all6_list = crop_image(img_800_all6, 6)


################ A = 600 ################
img_600_nodefects_all = cv2.imread(image_600_nodefects_all, 0)
img_600_nodefects_list = crop_image(img_600_nodefects_all, 3)

img_600_all = cv2.imread(image_600_all, 0)
img_600_defects_list = crop_image(img_600_all, 3)


img_600_nodefects_all6 = cv2.imread(image_600_all6_nodefects, 0)
img_600_nodefects_all6_list = crop_image(img_600_nodefects_all6, 6)

img_600_all6 = cv2.imread(image_600_all6_defects, 0)
img_600_defects_all6_list = crop_image(img_600_all6, 6)

################ A = 400 ################
img_400_nodefects_all = cv2.imread(image_400_nodefects_all, 0)
img_400_nodefects_list = crop_image(img_400_nodefects_all, 3)

img_400_all = cv2.imread(image_400_all, 0)
img_400_defects_list = crop_image(img_400_all, 3)

img_400_nodefects_all6 = cv2.imread(image_400_all6_nodefects, 0)
img_400_nodefects_all6_list = crop_image(img_400_nodefects_all6, 6)

img_400_all6 = cv2.imread(image_400_all6_defects, 0)
img_400_defects_all6_list = crop_image(img_400_all6, 6)
################ A = 200 ################
img_200_nodefects_all = cv2.imread(image_200_nodefects_all, 0)
img_200_nodefects_list = crop_image(img_200_nodefects_all, 3)

img_200_all = cv2.imread(image_200_all, 0)
img_200_defects_list = crop_image(img_200_all, 3)

img_200_nodefects_all6 = cv2.imread(image_200_all6_nodefects, 0)
img_200_nodefects_all6_list = crop_image(img_200_nodefects_all6, 6)

img_200_all6 = cv2.imread(image_200_all6_defects, 0)
img_200_defects_all6_list = crop_image(img_200_all6, 6)

############# DEFECTS #############################
# fig1 = plt.figure()
# index_number = 5
# img_list_all = [img_1000_defects_all6_list[index_number], img_800_defects_all6_list[index_number], img_600_defects_all6_list[index_number], img_400_defects_all6_list[index_number], img_200_defects_all6_list[index_number]]
# colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
# smooth = True
#
# #process_image_and_plot(img_list_all, 1, scale, colors, smooth, '-')
# plt.xlim(2, 28)
# plt.ylim(0.5,2)
#
# #########################
# fig2 = plt.figure()
# img_list_all = [img_1000_defects_all6_list,img_800_defects_all6_list,img_600_defects_all6_list,img_400_defects_all6_list,img_200_defects_all6_list]
# colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
# smooth = True
# for i in range(len(img_list_all)):
#     img_list = img_list_all[i]
#     color = colors[i]
#     fig = plt.figure()
#     process_image_and_plot_averages(img_list, 1, scale, color, smooth)
#
#     plt.xlim(2, 28)
#     plt.ylim(0.5,2)
#
#
# fig3 = plt.figure()
# colors = ['k', '#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
#
# # colors = ['k', '#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
# # smooth = False
# # process_image_and_plot(img_1000_defects_all6_not_indexed_list, 1, scale, colors, smooth, '-')
# # process_image_and_plot(img_1000_defects_all6_list, 1, scale, colors, smooth, '-')
#
#
#
# #### NO DEFECTS
# fig4 = plt.figure()
# index_number = 5
# img_list_all = [img_1000_nodefects_all6_list[index_number], img_800_nodefects_all6_list[index_number], img_600_nodefects_all6_list[index_number], img_400_nodefects_all6_list[index_number], img_200_nodefects_all6_list[index_number]]
# colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
# smooth = True
#
# #process_image_and_plot(img_list_all, 1, scale, colors, smooth, '-')
# plt.xlim(2, 28)
# plt.ylim(0.5,2)
#
#
# #########################
fig5 = plt.figure()
img_list_all = [img_1000_nodefects_all6_list,img_800_nodefects_all6_list,img_600_nodefects_all6_list,img_400_nodefects_all6_list,img_200_nodefects_all6_list]
colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
smooth = True
for i in range(len(img_list_all)):
    img_list = img_list_all[i]
    color = colors[i]
    fig = plt.figure()
    #process_image_and_plot_averages(img_list, 1, scale, color, smooth)

    plt.xlim(2, 28)
    plt.ylim(0.5,2)

#plt.show()


##################################### AVERAGE AREA DEVIATION vs ACCEL ###############
# def process_image_avgArea(img_list, number_filaments_per_image, scale):
#     black = 50  # upper range
#     white = 255  # upper range
#
#     num_white_pix_scalebar_dict = {}
#     num_blue_pix_filament_dict = {}
#     for j in range(len(img_list)):
#         pix_scalebar = {}
#         num_blue_pix_filament = {}
#
#         current_img = img_list[j]
#         for i in range(len(current_img)):
#             num_pix_total = len(current_img[i])
#             num_white_pix_scalebar = np.sum(current_img[3] == white)
#
#             num_white_pix = np.sum(current_img[i] >= white)
#             num_black_pix = np.sum(current_img[i] <= black)
#             num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)
#
#             pix_scalebar[i] = num_white_pix_scalebar / number_filaments_per_image
#
#
#             num_blue_pix_filament[i] = num_blue_pix / number_filaments_per_image
#
#         num_white_pix_scalebar_dict[j] = pix_scalebar
#         num_blue_pix_filament_dict[j] = num_blue_pix_filament
#
#     scale_bar_average_dict = {}
#     scale_bar_std_dict = {}
#     scaled_dict = {}
#     for i in range(len(num_white_pix_scalebar_dict)):
#         current_img = num_white_pix_scalebar_dict[i]
#         width_values = list(current_img.values())
#         scale_bar_width = np.average(width_values)
#         scale_bar_std = np.std(width_values)
#         scale_bar_average_dict[i] = scale_bar_width
#         scale_bar_std_dict[i] = scale_bar_std
#         scaled_dict[i] = scale / scale_bar_width
#     #print("scaled_dict = ", scaled_dict)
#
#     area_list = []
#     for i in range(len(num_blue_pix_filament_dict)):
#         current_fil = num_blue_pix_filament_dict[i]
#         area = 0
#         for j in range(len(current_fil)):
#             area += num_blue_pix_filament_dict[i][j] * scaled_dict[0] * scale
#
#         area_list.append(area/10590.725620567771)
#
#     average_area = np.average([area_list])
#     std_area = np.std([area_list])
#
#     return average_area, std_area
#
# img_list_all = [img_1000_defects_all6_list[1:],img_800_defects_all6_list[1:],img_600_defects_all6_list[1:],img_400_defects_all6_list[1:],img_200_defects_all6_list[1:]]
# avg_area_list = []
# std_area_list = []
#
# for i in range(len(img_list_all)):
#     img_list = img_list_all[i]
#     output = process_image_avgArea(img_list, 1, scale)
#     avg_area = output[0]
#     std_area = output[1]
#
#     avg_area_list.append(avg_area)
#     std_area_list.append(std_area)
#
# print(avg_area_list)
# print(std_area_list)
# print(np.average(avg_area_list))
# accel_list = [1000, 800, 600, 400, 200]
# colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']
#
# plt.plot(accel_list, avg_area_list, color = 'k', linewidth = 3)
# for i in range(len(avg_area_list)):
#     plt.errorbar(accel_list[i], avg_area_list[i], yerr = std_area_list[i], color = 'gray', linewidth = 2, capsize = 2)
#     plt.plot(accel_list[i], avg_area_list[i], color = colors[i], marker='o', markersize=7)
#
#
# img_list_all = [img_1000_nodefects_all6_list[1:],img_800_nodefects_all6_list[1:],img_600_nodefects_all6_list[1:],img_400_nodefects_all6_list[1:],img_200_nodefects_all6_list[1:]]
# avg_area_list = []
# std_area_list = []
#
# for i in range(len(img_list_all)):
#     img_list = img_list_all[i]
#     output = process_image_avgArea(img_list, 1, scale)
#     avg_area = output[0]
#     std_area = output[1]
#
#     avg_area_list.append(avg_area)
#     std_area_list.append(std_area)
#
# print(avg_area_list)
# print(std_area_list)
# print(np.average(avg_area_list))
#
# plt.plot(accel_list, avg_area_list, color = 'k', linewidth = 3, linestyle = '--')
# for i in range(len(avg_area_list)):
#     plt.errorbar(accel_list[i], avg_area_list[i], yerr = std_area_list[i], color = 'gray', linewidth = 2, capsize = 2)
#     plt.plot(accel_list[i], avg_area_list[i], color = colors[i], marker='s', markersize=7)
#
# plt.xlabel("Acceleration")
# plt.ylabel("Relative Area")

##################################### AVERAGE MAX PEAK vs ACCEL ###############
def process_image_avgMAX(img_list, number_filaments_per_image, scale):
    black = 50  # upper range
    white = 255  # upper range

    num_white_pix_scalebar_dict = {}
    num_blue_pix_filament_dict = {}
    for j in range(len(img_list)):
        pix_scalebar = {}
        num_blue_pix_filament = {}

        current_img = img_list[j]
        for i in range(len(current_img)):
            num_pix_total = len(current_img[i])
            num_white_pix_scalebar = np.sum(current_img[3] == white)

            num_white_pix = np.sum(current_img[i] >= white)
            num_black_pix = np.sum(current_img[i] <= black)
            num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)

            pix_scalebar[i] = num_white_pix_scalebar / number_filaments_per_image


            num_blue_pix_filament[i] = num_blue_pix / number_filaments_per_image

        num_white_pix_scalebar_dict[j] = pix_scalebar
        num_blue_pix_filament_dict[j] = num_blue_pix_filament

    scale_bar_average_dict = {}
    scale_bar_std_dict = {}
    scaled_dict = {}
    for i in range(len(num_white_pix_scalebar_dict)):
        current_img = num_white_pix_scalebar_dict[i]
        width_values = list(current_img.values())
        scale_bar_width = np.average(width_values)
        scale_bar_std = np.std(width_values)
        scale_bar_average_dict[i] = scale_bar_width
        scale_bar_std_dict[i] = scale_bar_std
        scaled_dict[i] = scale / scale_bar_width
    #print("scaled_dict = ", scaled_dict)

    import heapq
    max3_list = []
    for i in range(len(num_blue_pix_filament_dict)):
        current_fil = num_blue_pix_filament_dict[i]
        current_fil_list = list(current_fil.values())
        max3 = heapq.nlargest(3, current_fil_list)
        max3_scaled = [elem * (scaled_dict[i]) for elem in max3]

        max3_list.append(max3_scaled)

    average_max = np.average(max3_list)
    std_max = np.std(max3_list)

    return average_max, std_max
img_list_all = [img_1000_defects_all6_list[1:],img_800_defects_all6_list[1:],img_600_defects_all6_list[1:],img_400_defects_all6_list[1:],img_200_defects_all6_list[1:]]

avg_max_list = []
std_max_list = []
for i in range(len(img_list_all)):
    img_list = img_list_all[i]
    output = process_image_avgMAX(img_list, 1, scale)
    avg_max = output[0]
    std_max = output[1]

    avg_max_list.append(avg_max)
    std_max_list.append(std_max)

print(avg_max_list)
print(std_max_list)
accel_list = [1000, 800, 600, 400, 200]
colors = ['#2a4c8b', '#1e6fa1', '#0a95a6', '#59b97c', '#b9d14b']

fig = plt.figure()
plt.plot(accel_list, avg_max_list, color = 'k', linewidth = 3)
for i in range(len(avg_max_list)):
    plt.errorbar(accel_list[i], avg_max_list[i], yerr = std_max_list[i], color = 'gray', linewidth = 2, capsize = 2)
    plt.plot(accel_list[i], avg_max_list[i], color = colors[i], marker='o', markersize=7)


img_list_all = [img_1000_nodefects_all6_list[1:],img_800_nodefects_all6_list[1:],img_600_nodefects_all6_list[1:],img_400_nodefects_all6_list[1:],img_200_nodefects_all6_list[1:]]

avg_max_list = []
std_max_list = []
for i in range(len(img_list_all)):
    img_list = img_list_all[i]
    output = process_image_avgMAX(img_list, 1, scale)
    avg_max = output[0]
    std_max = output[1]

    avg_max_list.append(avg_max)
    std_max_list.append(std_max)

print(avg_max_list)
print(std_max_list)

plt.plot(accel_list, avg_max_list, color = 'k', linewidth = 3, linestyle = '--')
for i in range(len(avg_max_list)):
    plt.errorbar(accel_list[i], avg_max_list[i], yerr = std_max_list[i], color = 'gray', linewidth = 2, capsize = 2)
    plt.plot(accel_list[i], avg_max_list[i], color = colors[i], marker = 's',  markersize=7)

plt.xlabel("Acceleration")
plt.ylabel("Defect deviation from ideal (mm)")

plt.show()

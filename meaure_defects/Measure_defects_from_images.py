import numpy as np
import cv2
import matplotlib.pyplot as plt

scale = 2.5 # scale bar is 2.5 mm

image_1000_v1 = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_Sample1_removedglare.png'
image_1000_v2 = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_SAMPLE2.png'
image_1000_v3 = '230504_SCAN_.58mm_F20_PS1_A1000_2.5scalebar_python_SAMPLE3.png'

image_800_v1 = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_editglares_SAMPLE1.png'
image_800_v2 = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_editglares_SAMPLE2.png'
image_800_v3 = '230504_SCAN_.58mm_F20_PS1_A800_2.5scalebar_python_editglares_SAMPLE3.png'

image_600_v2 = '230504_SCAN_.58mm_F20_PS1_A600_2.5scalebar_python_editglares_SAMPLE2.png'

image_400_v2 = '230504_SCAN_.58mm_F20_PS1_A400_2.5scalebar_python_editglares_SAMPLE2.png'

image_200_v2 = '230504_SCAN_.58mm_F20_PS1_A200_2.5scalebar_python_editglares_SAMPLE2.png'

img_1000_v1 = cv2.imread(image_1000_v1, 0)
img_1000_v2 = cv2.imread(image_1000_v2, 0)
img_1000_v3 = cv2.imread(image_1000_v3, 0)


img_800_v1 = cv2.imread(image_800_v1, 0)
img_800_v2 = cv2.imread(image_800_v2,0)
img_800_v3 = cv2.imread(image_800_v3, 0)

img_600_v2 = cv2.imread(image_600_v2, 0)
img_400_v2 = cv2.imread(image_400_v2, 0)
img_200_v2 = cv2.imread(image_200_v2, 0)


#img_list = [img_1000_v2, img_1000_v3]
#img_list = [img_800_v2, img_800_v3]
#img_list = [ img_1000_v2, img_1000_v3, img_800_v2, img_800_v3]
#img_list = [img_1000_v1, img_1000_v2, img_1000_v3, img_800_v1, img_800_v2]
img_list = [img_1000_v2,img_800_v2, img_600_v2,  img_400_v2, img_200_v2]

black = 50  # upper range
white = 255 # upper range

# num_white_pix_scalebar = {}
# num_blue_pix_filament = {}

# for i in range(len(img_1000)):
#     num_pix_total = len(img_1000[i])
#     num_white_pix = np.sum(img_1000[i] >= white)
#     num_black_pix = np.sum(img_1000[i] <= black)
#     num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)
#
#     num_white_pix_scalebar[i] = num_white_pix
#     num_blue_pix_filament[i] = (num_pix_total - (num_black_pix + num_white_pix))
#
# print("num_white_pix_scalebar_A1000 = ", num_white_pix_scalebar)
# print("num_blue_pix_filament_A1000 = ", num_blue_pix_filament)
#
# dist_values = list(num_blue_pix_filament.keys())
# width_values = list(num_blue_pix_filament.values())
#
# plt.plot(dist_values, width_values)
# plt.show()

num_white_pix_scalebart_dict = {}
num_blue_pix_filament_dict = {}

for j in range(len(img_list)):
    pix_scalebar = {}
    num_blue_pix_filament = {}

    current_img = img_list[j]
    for i in range(len(img_1000_v1)):
        num_pix_total = len(current_img[i])
        num_white_pix_scalebar = np.sum(current_img[3] == white)

        num_white_pix = np.sum(current_img[i] >= white)
        num_black_pix = np.sum(current_img[i] <= black)
        num_blue_pix = num_pix_total - (num_black_pix + num_white_pix)

        pix_scalebar[i] = num_white_pix_scalebar
        num_blue_pix_filament[i] = (num_pix_total - (num_black_pix + num_white_pix))

    num_white_pix_scalebart_dict[j] = pix_scalebar
    num_blue_pix_filament_dict[j] = num_blue_pix_filament


scale_bar_dict = {}
scale_bar_std_dict = {}
scaled_dict = {}
for i in range(len(num_white_pix_scalebart_dict)):
    current_img = num_white_pix_scalebart_dict[i]
    width_values = list(current_img.values())
    scale_bar_width = np.average(width_values)
    scale_bar_std = np.std(width_values)
    scale_bar_dict[i] = scale_bar_width
    scale_bar_std_dict[i] = scale_bar_std

    scaled_dict[i] = scale/scale_bar_width



for i in range(len(num_blue_pix_filament_dict)):
    current_img = num_blue_pix_filament_dict[i]
    dist_values = list(current_img.keys())
    width_values = list(current_img.values())
    plt.plot(dist_values, width_values)




plt.show()

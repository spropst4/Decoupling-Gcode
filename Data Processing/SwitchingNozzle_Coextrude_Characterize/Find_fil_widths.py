'''
Author: Sarah Propst
Date: 10/5/23

Purpose: Count pixels to measure width of filaments

Photo Steps:
1. Index photos to black and white in photoshop (Image > Mode > Indexed Color...)
2. Save images as .png
3. Add images to same directory as python code

'''


import cv2 # if there is an error try importing as OpenCV
import csv
import numpy as np
import os
import matplotlib.pyplot as plt

def process_scale_bar(scale_bar_image, scale_length_mm):
    img = cv2.imread(scale_bar_image, 0)
    scale_length_pix = img.shape[0]
    scale_factor = scale_length_mm/scale_length_pix
    return scale_factor

def crop_images(image, scale_factor, export_path, sample_name, y_start, x_start, y_fil_length, x_spacing):
    #img = cv2.imread(image, 0)
    img = image
    y = int(y_start/scale_factor)
    h = int(y_fil_length/scale_factor)
    x = int(x_start/scale_factor)
    w = int(x_spacing/scale_factor)
    crop_img = img[y:y + h, x:x + w]
    cv2.imwrite(export_path + '\\' + sample_name +'.png', crop_img)

def process_total_filwidth(image, scale_factor):
    img = cv2.imread(image,0) # image into array of pixels
    #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # rotate 90' clockwise; comment out if your filaments are vertical

    num_width_pix_list = []
    num_row_list = []

    for row in range(len(img)):
        num_width_pix = np.sum(img[row] > 80)
        #num_width_pix = img.shape[1] - np.sum(img[row] == 0)  # counts pixels in the row that are equal to fil_color; if you don't index, you will need to change this to a range
        num_width_pix_list.append(num_width_pix * scale_factor) # counts the width of the filament
        num_row_list.append((row)*scale_factor) # counts the distance along the filaments

    return num_row_list, num_width_pix_list

def find_colors(image, scale_factor):
    img = cv2.imread(image, 0) # image into array of pixels
    #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # rotate 90' clockwise; comment out if your filaments are vertical
    #img = crop_images(image)
    pixel_color_list = []
    color_list = []
    width_list = []
    current_row_widths = []

    for row in range(len(img)):
        if 628 <= row <= len(img) - 628:
            pixel_color_list.append(list(img[row]))
            for pixel_count in range(len(img[row])):
                pixel = img[row][pixel_count]
                width = pixel_count*scale_factor
                current_row_widths.append(width)
                if pixel not in color_list:
                    color_list.append(pixel)

            width_list.append(current_row_widths)
            current_row_widths = []

    return pixel_color_list, color_list, width_list
def find_average_curve(list_of_lists):
   return [float(sum(col)) / len(col) for col in zip(*list_of_lists)]

def find_std_error(list_of_lists):
    std = [float(np.std(col)) for col in zip(*list_of_lists)]
    upperbound = [float(np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    lowerbound = [float(-np.std(col)+float(sum(col))/len(col)) for col in zip(*list_of_lists)]
    return std, upperbound, lowerbound

'''Scale Bar'''
scale_bar_image = 'Scale_bar_5mm_3200dpi.png'
scale_length_mm = 5
scale_factor = process_scale_bar(scale_bar_image, scale_length_mm)

'''Images'''
path = "Coextrude_03"
file_list = os.listdir(path)
print('file_list = ', file_list)
image_list = []
for elem in file_list:
    if '.png' in elem:
        image_list.append(elem)
print('image_list = ', image_list)

'''Process cropped images'''
width_list  = []
for i in range(len(image_list)):
    #print('plotting ', image_list[i])
    image = path + '\\' + image_list[i]

    '''Widths'''
    width_results = process_total_filwidth(image, scale_factor)
    current_width_list = width_results[1]
    current_total_avg_width = np.average(current_width_list)
    print(image_list[i], current_total_avg_width)
    width_list.append(current_total_avg_width)

# coestrude 1
x = [1,
0.952380952,
0.906976744,
0.863636364,
0.822222222,
0.782608696,
0.744680851,
0.708333333,
0.673469388,
0.64,
0.607843137
]

# coextrude 2
x = [1,
0.953488372,
0.909090909,
0.866666667,
0.826086957,
0.787234043,
0.75,
0.714285714,
0.68,
0.647058824,
0.615384615
]

# coextrude 3
x = [1,
1.048780488,
1.1,
1.153846154,
1.210526316,
1.27027027,
1.333333333,
1.4,
1.470588235,
1.545454545,
1.625
]



plt.plot(x,width_list, marker = 'o')
fig = plt.figure()
plt.plot(width_list, marker = 's')
plt.show()

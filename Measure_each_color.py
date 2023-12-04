'''
Author: Sarah Propst
Date: 12/3/2023

Purpose: This code determines the width of the total filament, the width of color1 in the filament, and the width of color2 in the filament.

It processes all images that were cropped using CropImages.py
'''


import cv2 # if there is an error try importing as OpenCV
import csv
import numpy as np
import os
import matplotlib.pyplot as plt
import pandas as pd
import matplotlib as mpl
from matplotlib.backends.backend_pdf import PdfPages

def process_scale_bar(scale_bar_image, scale_length_mm):
    img = cv2.imread(scale_bar_image, 0)
    scale_length_pix = img.shape[0]
    scale_factor = scale_length_mm/scale_length_pix
    return scale_factor
def find_and_measure_each_color(image, color1_range, color2_range, scale_factor):
    img = cv2.imread(image, 0) # image into array of pixels
    #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # rotate 90' clockwise; comment out if your filaments are vertical

    pixel_color_list = []
    color1_width_list = []
    color2_width_list = []
    color1_count = 0
    color2_count = 0
    for row in range(len(img)):
        pixel_color_list.append(list(img[row]))
        for pixel_count in range(len(img[row])):
            pixel = img[row][pixel_count]
            if pixel == color1_range:
                color1_count += 1
            elif pixel == color2_range:
                color2_count += 1

        color1_width_list.append(color1_count*scale_factor)
        color2_width_list.append(color2_count*scale_factor)
        color1_count = 0
        color2_count = 0

    return color1_width_list, color2_width_list


'''Scale Bar'''
scale_bar_image = 'Scale_bar_5mm_3200dpi.png'
scale_length_mm = 5
scale_factor = process_scale_bar(scale_bar_image, scale_length_mm)

'''Images'''
color1_range = 110 # red
color2_range = 162 # blue
path = "IndexedCoextrude_03"
file_list = os.listdir(path)
print('file_list = ', file_list)
image_list = []
for elem in file_list:
    if '.png' in elem:
        image_list.append(elem)
print('image_list = ', image_list)

pressure_path = 'IndexedCoextrude_03/IndexedCoextrude_03_Pressures.txt'

'''Process cropped images'''
color1_avg_width_list = []
color2_avg_width_list = []
color1_std_list = []
color2_std_list = []
total_width_list = []
for i in range(len(image_list)):
    print('processing ', image_list[i])
    images = path + '\\' + image_list[i]

    '''Colors'''
    color_results = find_and_measure_each_color(images, color1_range, color2_range, scale_factor)
    current_color1_width_list = color_results[0]
    current_color2_width_list = color_results[1]

    current_color1 = np.average(current_color1_width_list)
    current_color2 = np.average(current_color2_width_list)

    current_color1_std = np.std(current_color1_width_list)
    current_color2_std = np.std(current_color2_width_list)

    total_current_width = current_color1 + current_color2

    color1_avg_width_list.append(current_color1)
    color2_avg_width_list.append(current_color2)

    color1_std_list.append(current_color1_std)
    color2_std_list.append(current_color2_std)

    total_width_list.append(total_current_width)

'''Write data to csv'''
export_file = (path + '\\' + 'Results_' + path + '.csv')  # file name to export the results as csv
col_labels = ['color1_avg_width_list', 'color2_avg_width_list', 'color1_std_list', 'color2_std_list','total_width_list']
data = zip(color1_avg_width_list, color2_avg_width_list, color1_std_list, color2_std_list, total_width_list)

print('writing to ', export_file)
with open(export_file, "w") as f:
    writer = csv.writer(f)
    writer.writerow(col_labels)
    for row in data:
        writer.writerow(row)


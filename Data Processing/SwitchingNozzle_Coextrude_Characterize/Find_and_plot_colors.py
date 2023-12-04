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
        num_width_pix = img.shape[1] - np.sum(img[row] > 50)  # counts pixels in the row that are equal to fil_color; if you don't index, you will need to change this to a range
        num_width_pix_list.append(num_width_pix * scale_factor) # counts the width of the filament
        num_row_list.append((row)*scale_factor) # counts the distance along the filaments

    return num_row_list, num_width_pix_list

def find_colors(image, scale_factor):
    img = cv2.imread(image, 0) # image into array of pixels
    #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # rotate 90' clockwise; comment out if your filaments are vertical

    pixel_color_list = []
    color_list = []
    width_list = []
    current_row_widths = []

    for row in range(len(img)):
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
path = "IndexedCoextrude_03"
file_list = os.listdir(path)
print('file_list = ', file_list)
image_list = []
for elem in file_list:
    if '.png' in elem:
        image_list.append(elem)
print('image_list = ', image_list)

image_list = [image_list[-1]]
'''Process cropped images'''
for i in range(len(image_list)):
    print('plotting ', image_list[i])
    images = path + '\\' + image_list[i]

    '''Colors'''
    color_results = find_colors(images, scale_factor)
    pixel_color_list = color_results[0]
    color_list = color_results[1]
    width_list = color_results[2]

    print(sorted(color_list))

    avg_color = pixel_color_list[len(pixel_color_list)//2]#find_average_curve(pixel_color_list)
    std = find_std_error(pixel_color_list)
    std_lower = std[2]
    std_upper = std[1]
    plt.plot(width_list[0], avg_color, marker = 'o')
    plt.fill_between(width_list[0], std_lower,std_upper , alpha = 0.15)


plt.show()

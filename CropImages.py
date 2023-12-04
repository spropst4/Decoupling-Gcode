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

def process_image(image, scale_factor, fil_color):
    img = cv2.imread(image) # image into array of pixels
    #img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) # rotate 90' clockwise; comment out if your filaments are vertical

    num_width_pix_list = []
    num_row_list = []

    for row in range(len(img)):
        num_width_pix = np.sum(img[row] == fil_color)  # counts pixels in the row that are equal to fil_color; if you don't index, you will need to change this to a range
        num_width_pix_list.append(num_width_pix * scale_factor) # counts the width of the filament
        num_row_list.append((row)*scale_factor) # counts the distance along the filaments

    return num_row_list, num_width_pix_list

'''Scale Bar'''
scale_bar_image = 'Scale_bar_5mm_3200dpi.png'
scale_length_mm = 5
scale_factor = process_scale_bar(scale_bar_image, scale_length_mm)
print(scale_factor)

'''Images'''
path = "C:\\Users\\sprop\\OneDrive\\Desktop\\SwitchingCoextrude_PythonImages"

image_list = os.listdir(path)
print(image_list)

'''Crop images into folder'''
images = path + '\\' + image_list[3]
export_path = 'IndexedCoextrude_03'

img = cv2.imread(images,0)
img = cv2.flip(img, 1)
x_start = 0
y_start = 25
y_fil_length = 100
x_spacing = 3
sample_name = 1
while x_start/scale_factor <= img.shape[1]:
    if sample_name < 10:
        add_sample_id = '_0'
    else:
        add_sample_id = '_'
    crop_images(img, scale_factor, export_path, export_path + add_sample_id + str(sample_name), y_start, x_start, y_fil_length, x_spacing)
    x_start += x_spacing
    sample_name += 1

print('cropped the images...')

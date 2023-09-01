'''
Author: Sarah Propst
Date: 8/31/23
'''
# This function creates a gradient infill of a square lattice

import numpy as np
import cv2
def ImageLattice(image, fil_spacing, num_layers):
    black = 0
    white = 255
    black_thresh = 55
    prev_pixel = white
    turn_dist = 0
    first_turn = False
    for layer in range(num_layers):
        img = cv2.imread(image, 0)  #### fill in rest
        # if (layer +1)%2 != 0: # odd layer
        #     img = cv2.imread(image, 0) #### fill in rest
        #
        # else:
        #     img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE) ### rotate 90' fill in rest

        img_shape = img.shape
        num_filaments = img_shape[0] # height
        num_pixels = img_shape[1] # width


        strut_dist = 0

        for fil in range(num_filaments):
            if (layer + 1) % 2 != 0:  # odd layer
                if layer > 0:
                    if fil == 0:
                        x_sign_odd_layer = -x_sign_even_layer
                    else:
                        x_sign_odd_layer = -x_sign_odd_layer

                    y_sign_odd_row = -y_sign_even_layer
                    # if (fil + 1) % 2 != 0:  # odd fil
                    #     x_sign_odd_layer = -x_sign_even_layer
                    # else:
                    #     x_sign_odd_layer = -x_sign_odd_layer

                else:
                    y_sign_odd_row = 1
                    if fil == 0:
                        x_sign_odd_layer = 1
                    else:
                        x_sign_odd_layer = -x_sign_odd_layer

                for pix in range(num_pixels):
                    pixel = img[fil][pix]

                    if pixel <= black_thresh:
                        strut_dist += 1 * fil_spacing


                    if pixel > black_thresh and prev_pixel <= black_thresh:
                        strut_dist = x_sign_odd_layer * strut_dist
                        strut_var = 'X'
                        
                        turn_dist = y_sign_odd_row * fil_spacing
                        turn_var = 'Y'


                        print('G1 ' + strut_var + str(strut_dist))
                        print('G1 ' + turn_var + str(turn_dist))

                        strut_dist = 0
                    prev_pixel = pixel
            else:
                x_sign_even_layer = x_sign_odd_layer * -1  # reverses the x-direction
                if fil == 0:  # odd fil
                    y_sign_even_layer= -y_sign_odd_row
                else:
                    y_sign_even_layer = -y_sign_even_layer

                for pix in range(num_pixels):
                    pixel = img[fil][pix]
                    if pixel <= black_thresh:
                        strut_dist += 1*fil_spacing

                    if pixel > black_thresh and prev_pixel <= black_thresh:

                        strut_dist = y_sign_even_layer * strut_dist
                        strut_var = 'Y'

                        turn_dist = x_sign_even_layer * fil_spacing
                        turn_var = 'X'


                        print('G1 ' + strut_var + str(strut_dist))
                        print('G1 ' + turn_var + str(turn_dist))

                        strut_dist = 0
                    prev_pixel = pixel

        print('G1 Z1')
        print('G90')
        print('G1 X0 YO')
        print('G91')



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    image = "img_1.png"
    fil_spacing = 1
    num_layers = 2
    ImageLattice(image, fil_spacing, num_layers)
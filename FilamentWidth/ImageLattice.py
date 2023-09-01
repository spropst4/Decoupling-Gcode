'''
Author: Sarah Propst
Date: 8/31/23
'''
# This function creates a gradient infill of a square lattice

import numpy as np

def ImageLattice():
    for layer in range(num_layers):
        if (layer +1)%2 != 0: # odd layer
            img = cv2. #### fill in rest

        else:
            img = cv2. ### rotate 90' fill in rest

        num_filaments = img.shape() ### number of columns
        num_pixels = img.shape() ### number of rows
        for fil in range(num_filaments):
            if (layer + 1) % 2 != 0:  # odd layer
                if layer > 0:
                    y_sign_odd_row = -y_sign_even_row
                    if (fil + 1) % 2 != 0:  # odd fil
                        x_sign_odd_row = -x_sign_even_row
                    else:
                        x_sign_odd_row = -x_sign_odd_row

                else:
                    y_sign_odd_row = 1
                    if (fil + 1) % 2 != 0:  # odd fil
                        x_sign_odd_row = 1
                    else:
                        x_sign_odd_row = -1

                for pix in range(num_pixels):
                    if pixel != prev_pixel:
                        strut_dist += 1

                        strut_dist = x_sign_odd_row * strut_dist
                        strut_var = 'X'

                        turn_dist = y_sign_odd_row * fil_spacing
                        turn_var = 'Y'

            else:
                x_sign_even_row = x_sign_odd_row * -1  # reverses the x-direction
                if (fil + 1) % 2 != 0:  # odd fil
                    y_sign_even_row = -y_sign_odd_row
                else:
                    y_sign_even_row = -y_sign_even_row

                for pix in range(num_pixels):
                    if pixel != prev_pixel:
                        strut_dist += 1

                        strut_dist = y_sign_even_row * strut_dist
                        strut_var = 'Y'

                        turn_dist = x_sign_even_row * fil_spacing
                        turn_var = 'X'


# Press the green button in the gutter to run the script.
if __name__ == '__main__':

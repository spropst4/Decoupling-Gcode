import cv2
import numpy as np

'''Reverse print prints a snake pattern and reverse direction after each layer '''
def image_2_gcode_CheckerboardCube_reverseprint(image_name, fil_width,checker_size, color_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, export_txt_file):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    img = cv2.imread(image_name, 0)

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []
    dist_list = []
    command_list = []

    first_toggle_ON = True

    layer_count = 0

    first_image = img
    second_image = cv2.bitwise_not(img)

    first_image_ON = True
    current_image = first_image

    for layers in range(img.shape[0]):

        if (layers + 1) % 2 == 0:  # even layers
            y_sign = -1
        else:  # odd layers:
            y_sign = 1

        if layer_count == checker_size:
            layer_count =0
            if first_image_ON == True:
                current_image = second_image
                first_image_ON = False

            else:
                current_image = first_image
                first_image_ON = True

        layer_count += 1

        for i in range(len(current_image)):  # number of rows of pixels  (image height)
            current_image_row = current_image[i]

            if (i + 1) % 2 == 0:  # even rows:
                current_image_row = np.flip(current_image_row)  # reverse order of pixel
                dist_sign = -1  # reverse x-direction of print
            else:  # odd rows:
                dist_sign = 1

            for j in range(len(current_image_row)):  # number of pixels in a row (image width)
                pixel = current_image_row[j]

                if prev_pixel != pixel:
                    for k in range(len(color_list)):
                        color = color_list[k]

                        if pixel == color:
                            color_ON = color_ON_list[k]
                            color_OFF = color_OFF_list[k]

                    if dist != 0:
                        gcode_list.append(gcode)
                        dist_list.append(dist_sign * dist)

                    else:
                        gcode_list.append('')
                        dist_list.append('')


                    if first_toggle_ON == False:
                        command_list.append([color_ON, prev_color_OFF])
                    else:
                        command_list.append([color_ON])
                        first_toggle_ON = False

                    dist = 0

                    gcode = 'G1 X'
                    if pixel == gcode_simulate_color:
                        gcode = gcode_color1


                dist += fil_width

                prev_pixel = pixel
                prev_color_OFF = color_OFF

            gcode_list.append(gcode)
            dist_list.append(dist_sign * dist)
            command_list.append('')

            if (i+1) != len(img):
                gcode_list.append('G1 Y')
                dist_list.append(y_sign * fil_width)
                command_list.append('')
            else:
                gcode_list.append('G1 Z')
                dist_list.append(fil_width)
                command_list.append('')

            dist = 0

    gcode_list.append('')
    dist_list.append('')
    command_list.append([color_OFF])

    f = open(export_txt_file + '_reversePrint.txt', 'w')
    f.write('\n\rG91')
    for i in range(len(gcode_list)):
        f.write('\n\r' + str(gcode_list[i]) + str(dist_list[i]))
        for elem in command_list[i]:
            f.write('\n\r' + str(elem))

'''Lattice print prints a lattice structure'''
def image_2_gcode_CheckerboardCube_latticeprint(image_name, fil_width,checker_size, color_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, export_txt_file):
    if gcode_simulate == True:
        gcode_color1 = "G0 "
    else:
        gcode_color1 = "G1 "

    img = cv2.imread(image_name, 0)

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []
    var_list = []
    dist_list = []
    command_list = []
    first_toggle_ON = True

    layer_count = 0

    first_image = img
    second_image = cv2.bitwise_not(img)
    cv2.imwrite('CheckImage__cube.png', second_image)

    first_image_ON = True
    current_image = first_image
    short_move_sign = 1
    dist_sign = 1

    for layers in range(img.shape[0]):

        if (layers + 1) % 2 == 0:  # even layers
            long_move_sign = -1*short_move_sign
            short_move_sign = -1*dist_sign

            long_dist_var = 'Y'
            short_dist_var = 'X'

        else:  # odd layers:
            long_move_sign = -1*short_move_sign
            short_move_sign = -1*dist_sign


            long_dist_var = 'X'
            short_dist_var = 'Y'

        if layer_count == checker_size:
            layer_count =0
            if first_image_ON == True:
                current_image = second_image
                first_image_ON = False

            else:
                current_image = first_image
                first_image_ON = True

        layer_count += 1

        for i in range(len(current_image)):  # number of rows of pixels  (image height)
            current_image_row = current_image[i]


            if (i + 1) % 2 == 0:  # even rows:
                current_image_row = np.flip(current_image_row)  # reverse order of pixel
                dist_sign = -1*long_move_sign  # reverse of print

            else:  # odd rows:
                dist_sign = 1*long_move_sign

            for j in range(len(current_image_row)):  # number of pixels in a row (image width)
                pixel = current_image_row[j]

                if prev_pixel != pixel:
                    for k in range(len(color_list)):
                        color = color_list[k]

                        if pixel == color:
                            color_ON = color_ON_list[k]
                            color_OFF = color_OFF_list[k]

                    if dist != 0:
                        gcode_list.append(gcode)
                        var_list.append(long_dist_var)
                        dist_list.append(dist_sign * dist)

                    else:
                        gcode_list.append('')
                        var_list.append('')
                        dist_list.append('')


                    if first_toggle_ON == False:
                        command_list.append([color_ON, prev_color_OFF])
                    else:
                        command_list.append([color_ON])
                        first_toggle_ON = False

                    dist = 0

                    gcode = 'G1 '
                    if pixel == gcode_simulate_color:
                        gcode = gcode_color1


                dist += fil_width

                prev_pixel = pixel
                prev_color_OFF = color_OFF

            gcode_list.append(gcode)
            var_list.append(long_dist_var)
            dist_list.append(dist_sign * dist)
            command_list.append('')

            if (i+1) != len(img):
                gcode_list.append(gcode)
                var_list.append(short_dist_var)
                dist_list.append(short_move_sign * fil_width)
                command_list.append('')
            else:
                gcode_list.append(gcode)
                var_list.append('Z')

                dist_list.append(fil_width)
                command_list.append('')

            dist = 0
    gcode_list.append('')
    var_list.append('')

    dist_list.append('')
    command_list.append([color_OFF])

    f = open(export_txt_file + '_latticePrint.txt', 'w')
    f.write('\n\rG91')
    for i in range(len(gcode_list)):
        f.write('\n\r' + str(gcode_list[i]) + str(var_list[i])+ str(dist_list[i]))
        for elem in command_list[i]:
            f.write('\n\r' + str(elem))

## Grayscale:
black = 0
white = 255

####################################################################### Reverse PRINT #######################################################################

image_name = 'checkerboard_30x30pix.png'
export_txt_file = 'checkerboard_30x30pix_cube'
fil_width = 1  # width of filament/nozzle
checker_size = 6

color1 = black
color2 = white

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'

color_list = [color1, color2]
color_ON_list = [color1_ON, color2_ON]
color_OFF_list = [color1_OFF, color2_OFF]

output = image_2_gcode_CheckerboardCube_reverseprint(image_name, fil_width, checker_size, color_list, color_ON_list,color_OFF_list, gcode_simulate, gcode_simulate_color, export_txt_file)


####################################################################### LATTICE PRINT #######################################################################

image_name = 'checkerboard_30x30pix.png'
gcode_export = 'checkerboard_30x30pix_cube'
fil_width = 1  # width of filament/nozzle
checker_size = 6 # how many squares per row and column?

color1 = black
color2 = white

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1

color1_ON = 'Black ON'
color1_OFF = 'Black OFF'
color2_ON = 'White ON'
color2_OFF = 'White OFF'


color_list = [color1, color2]
color_ON_list = [color1_ON, color2_ON]
color_OFF_list = [color1_OFF, color2_OFF]

output = image_2_gcode_CheckerboardCube_latticeprint(image_name, fil_width, checker_size, color_list, color_ON_list,color_OFF_list, gcode_simulate, gcode_simulate_color, export_txt_file)

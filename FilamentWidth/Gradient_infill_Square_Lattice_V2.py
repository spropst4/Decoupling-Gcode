'''
Author: Sarah Propst
Date: 8/31/23
'''
# This function creates a gradient infill of a square lattice

import numpy as np

def Gradient_line_segmentation(input_line, segments, pressure_range):
    input_variables = input_line[0]
    input_dist = input_line[1]

    ### calculate line length
    line_length = 0
    for elem in input_dist:
        line_length += elem**2
    line_length = np.sqrt(line_length)


    pressure = pressure_range[1]
    ### determine number and length of the segments
    num_segments = segments[1]
    segment_len = segments[1]
    if segments[0] == 'length':
        num_segments = line_length/segment_len
        remainder = line_length%segment_len # returns the remainder
        first_n_last_segment_len = segment_len + remainder/2
        num_segments = int(line_length // segment_len) # returns the largest integer not greater than the exact division result

    else:
        segment_len = line_length/num_segments
        first_n_last_segment_len = segment_len
    print('------num-segments', num_segments)
    if num_segments%2 != 0:
        odd_extra = 1
        even_extra = 0
    else:
        odd_extra = 0
        even_extra = 1


    pressure_incr = (pressure_range[1] - pressure_range[0]) / ((num_segments//2 - even_extra))
    distance_count = 0
    pressure = pressure_range[1]
    pressure_gradient_region = line_length // 2
    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])
            distance_count += segment_len

            if segment_len < distance_count <= pressure_gradient_region + odd_extra:
                pressure -= pressure_incr

            elif pressure < pressure_range[1]:
                pressure += pressure_incr

            print('Pressure = ', round(pressure, 2))
            if (i+1) == num_segments or (i+1) == 1:
                print('G1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                print('G1 ' + input_variables[0] + str(sign * segment_len))



    elif len(input_dist) == 2: # sloped lines
        line_slope = abs(input_dist[1] / input_dist[0])
        a_sign = input_dist[0] / abs(input_dist[0])
        b_sign = input_dist[1] / abs(input_dist[1])

        for i in range(num_segments):
            a_segment = segment_len / np.sqrt(1 + line_slope ** 2)
            b_segment = line_slope * a_segment
            if (i+1) == num_segments or (i+1) == 1:
                a_segment = first_n_last_segment_len / np.sqrt(1 + line_slope ** 2)
                b_segment = line_slope * a_segment

            if segment_len < distance_count <= pressure_gradient_region + odd_extra:
                pressure -= pressure_incr

            elif pressure < pressure_range[1]:
                pressure += pressure_incr

            print('Pressure = ', round(pressure, 2))

            print('G1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))
def gradient_square_lattice(fil_spacing, num_filaments, num_layers, fil_width, layer_height, pressure_range):
    length = ((num_filaments-1)*fil_spacing)
    distance_list = []
    var_list = []

    for layer in range(num_layers):
        seg_number = 0
        even_extra = 0
        if num_filaments % 2 == 0:
            even_extra = 1

        pressure_change_between_midpoints = (pressure_range[1] - pressure_range[0]) / (num_filaments // 2 - even_extra)

        for fil in range(num_filaments):
            print(';----new FIL')
            if num_filaments%2 != 0: # if odd number of filaments
                odd_extra = 1
            else:
                odd_extra = 0

            if (fil + 1) == 1:
                dist_from_center = (num_filaments // 2) - (even_extra)
                mid_point_pressure = pressure_range[1]

            elif (fil+ 1) <= num_filaments//2 + odd_extra:
                dist_from_center -= 1
                mid_point_pressure -= pressure_change_between_midpoints

            elif (fil+ 1) == num_filaments//2 + even_extra:
                dist_from_center = dist_from_center

            else:
                dist_from_center += 1
                mid_point_pressure += pressure_change_between_midpoints

            print(';-------------------', round(mid_point_pressure,2))
            pressure_range_filament = [mid_point_pressure, pressure_range[1]]

            segments = ['length', fil_spacing]

            if (layer + 1)%2 != 0: # odd layer
                if layer > 0:
                    y_sign_odd_row = -y_sign_even_row
                    if (fil+1)%2 != 0: # odd fil
                        x_sign_odd_row = -x_sign_even_row
                    else:
                        x_sign_odd_row = -x_sign_odd_row

                else:
                    y_sign_odd_row = 1
                    if (fil + 1) % 2 != 0:  # odd fil
                        x_sign_odd_row = 1
                    else:
                        x_sign_odd_row = -1

                x_dist = x_sign_odd_row * length
                y_dist = y_sign_odd_row*fil_spacing


                input_line = [['X'], [x_dist]]
                Gradient_line_segmentation(input_line, segments, pressure_range_filament)

                # distance_list.append([x_dist])
                # var_list.append(['X'])

                if (fil + 1) != num_filaments:
                    distance_list.append([y_dist])
                    var_list.append(['Y'])
                    print('G1 Y' + str(y_dist))

            else:
                x_sign_even_row = x_sign_odd_row * -1 # reverses the x-direction
                if (fil+1)%2 != 0: # odd fil
                    y_sign_even_row = -y_sign_odd_row
                else:
                    y_sign_even_row = -y_sign_even_row

                x_dist = x_sign_even_row * fil_spacing
                y_dist = y_sign_even_row * length


                input_line = [['Y'], [y_dist]]
                Gradient_line_segmentation(input_line, segments, pressure_range_filament)

                # distance_list.append([y_dist])
                # var_list.append(['Y'])
                if (fil + 1) != num_filaments:
                    distance_list.append([x_dist])
                    var_list.append(['X'])
                    print('G1 X' + str(x_dist))

        distance_list.append([layer_height])
        var_list.append(['Z'])

        print('G1 Z' +str(layer_height))

    # for i in range(len(distance_list)):
    #     print('G1 ' + str(var_list[i][0]) + str(distance_list[i][0]))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    fil_spacing = 2
    num_filaments = 21
    num_layers = 10
    fil_width = 1
    layer_height = 1
    pressure_range = [22, 30]
    gradient_square_lattice(fil_spacing, num_filaments, num_layers, fil_width, layer_height, pressure_range)

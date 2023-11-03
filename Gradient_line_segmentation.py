'''
Author: Sarah Propst
Date: 8/28/23
'''
# This function divides any line into desired length/size of segments
# Intended for use with continuous gradients

import numpy as np
def open_gcode(gcode_txt):
    gcode_list = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            gcode_list.append(myline.strip('\n'))
        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        gcode_list = [x for x in gcode_list if ";--" not in x]  # removes comments
        gcode_list = [x for x in gcode_list if "---" not in x]  # removes comments

        gcode.close()
        return gcode_list
def find_distances(gcode_list):  # s = string to search, ch = character to find
    # ch = character to find
    var_list = ['X', 'Y', 'Z']
    input_line_list = []
    input_var_list = []

    for line in gcode_list:
        gcode_line = line.split(" ")
        result_dist_list = []
        result_var_list = []
        for elem in enumerate(gcode_line):
            for var in var_list:
                if var in elem[1]:
                    result = float(elem[1].strip(var))  # finds location of character, strips it, and outputs numerical number
                    result_dist_list.append(result)
                    result_var_list.append(var)

        input_line_list.append(result_dist_list)
        input_var_list.append(result_var_list)

    return input_var_list, input_line_list
def Gradient_line_segmentation(input_line, segments):
    input_variables = input_line[0]
    input_dist = input_line[1]

    ### calculate line length
    line_length = 0
    for elem in input_dist:
        line_length += elem**2
    line_length = np.sqrt(line_length)

    ### determine number and length of the segments
    num_segments = segments[1]
    segment_len = segments[1]
    if segments[0] == 'length':
        num_segments = line_length/segment_len
        remainder = line_length%segment_len # returns the remainder
        first_n_last_segment_len = segment_len + remainder/2
        num_segments = int(line_length // segment_len) # returns the largest integer not greater than the exact division result

    else:
        segment_len_input = line_length/num_segments
        first_n_last_segment_len = segment_len

    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])
            print('change pressure')
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

            print('change pressure')
            print('G1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gcode_txt = 'test_gcode.txt'
    gcode_list = open_gcode(gcode_txt)
    input_line_list = find_distances(gcode_list)

    segments = ['length', .56] # ['type', value], type options: 'length', 'number'
    for i in range(len(input_line_list[0])):
        input_line = [input_line_list[0][i], input_line_list[1][i]]
        Gradient_line_segmentation(input_line, segments)



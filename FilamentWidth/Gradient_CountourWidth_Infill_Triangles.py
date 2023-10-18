'''
Author: Sarah Propst
Date: 10/13/23
'''
# This function divides any line into desired length/size of segments
# Intended for use with continuous gradients

import numpy as np
def setpress(pressure):
    # IMPORTS
    from codecs import encode
    from textwrap import wrap

    pressure = str(int(pressure * 10))
    length = len(pressure)
    while length < 4:
        pressure = "0" + pressure
        length = len(pressure)

    commandc = bytes(('08PS  ' + pressure), "utf-8")

    # FIND CHECKSUM
    startc = b'\x05\x02'
    endc = b'\x03'

    hexcommand = encode(commandc, "hex")  # encode should turn this into a hex rather than ascii

    hexcommand = hexcommand.decode("utf-8")  # decode should turn this into a string object rather than a bytes object

    ####format for arduino#####
    format_command = str(hexcommand)
    format_command = '\\x'.join(format_command[i:i + 2] for i in range(0, len(format_command), 2))
    format_command = '\\x'+format_command
    ##########################

    hexcommand = wrap(hexcommand,
                      2)  # wrap should split the string into a horizontal array of strings of 2 characters each

    # GETTING THE 8 BIT 2'S COMPLEMENT
    decimalsum = 0
    for i in hexcommand:  # get the decimal sum of the hex command
        decimalsum = decimalsum + int(i, 16)
    checksum = decimalsum % 256  # get the remainder of the decimal sum
    checksum = bin(checksum)  # turn into binary
    checksum = checksum[2:]  # checksum is a string
    while len(checksum) < 8:  # checksum must represents 8 bits of information
        checksum = "0" + checksum
    invert = ""
    for i in checksum:  # binary sum must be inverted
        if i == '0':
            invert = invert + "1"
        else:
            invert = invert + "0"
    invert = int(invert, 2)  # binary sum turned into decimal form
    invert = invert + 1
    # CHECKSUM HAS BEEN RETRIEVED IN DECIMAL FORM
    checksum = invert
    checksum = hex(checksum)  # checksum is in the format "0x##"
    # CHECKSUM IS NOW IN ASCII FORM, don't be mislead by the hex function
    checksum = checksum[2:]
    checksumarray = []
    for i in checksum:  # must get alphabetical characters in uppercase for ascii to hex conversion
        if i.isalpha():
            i = i.upper()
            checksumarray.append(i)
        else:
            checksumarray.append(i)
    checksum = ""
    for i in checksumarray:
        checksum = checksum + i
    # checksum is a string.
    checksum = bytes(checksum, 'ascii')

    ####format for arduino#####
    hexchecksum = encode(checksum, 'hex')
    hexchecksum = hexchecksum.decode("utf-8")  # decode should turn this into a string object rather than a bytes object
    format_checksum = str(hexchecksum)  # format for arduino
    format_checksum = '\\x'.join(format_checksum[i:i + 2] for i in range(0, len(format_checksum), 2))
    format_checksum = '\\x' + format_checksum

    # SENDING OUT THE COMMAND
    ##format for arduino####
    finalcommand = ("\\x05\\x02") + format_command + format_checksum + str("\\x03")
    finalcommand = finalcommand.strip('\r').strip('\n')
    finalcommand = "b'" + finalcommand + "'"
    return finalcommand
def togglepress():
    # IMPORTS
    import serial
    from codecs import encode
    from textwrap import wrap
    toggle = str("b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03'")
    return toggle

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

#isosceles triangle
def triangle_isos(export_file_txt,x_y_ratio, outer_length,inner_length, fil_width):
    with open(export_file_txt, "w") as f:
        length = outer_length
        x = length / 2
        y = x_y_ratio*x
        #y = np.sqrt(length ** 2 - x ** 2)
        f.write('\n\rG91')

        f.write('\n\rG1 X' + str(x) + ' Y' + str(y))
        f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))
        length -= fil_width
        f.write('\n\rG1 X' + str(-length))

        slope = y / x

        while length > inner_length:
            length -= fil_width
            x = length / 2
            y = x * slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(y))

            length -= (2/x_y_ratio)*fil_width

            x = length / 2
            y = x * slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))

            length -= fil_width

            f.write('\n\rG1 X' + str(-length))

#equilateral triangle
def triangle_equi(export_file_txt, outer_length,inner_length, fil_width):
    with open(export_file_txt, "w") as f:
        length = outer_length
        x = length / 2
        y = np.sqrt(length ** 2 - x ** 2)
        f.write('\n\rG91')


        f.write('\n\rG1 X' + str(x) + ' Y' + str(y))
        f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))
        length -= fil_width
        f.write('\n\rG1 X' + str(-length))
        slope = y / x
        while length > inner_length:
            x = (length - fil_width) / 2
            y = x * slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(y))

            x -= 0.5*fil_width
            y = x * slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))

            length -= 3*fil_width

            f.write('\n\rG1 X' + str(-length))


def Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF):
    input_variables = input_line[0]
    input_dist_original = input_line[1]
    input_dist = []
    for elem in input_dist_original:
        if elem != 0:
            input_dist.append(elem)

    ### calculate line length
    line_length = 0
    for elem in input_dist:
        line_length += elem ** 2
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

    if num_segments%(1/gradient_fraction) == 0:
        pressure_divide = num_segments//(1/gradient_fraction) - 1
    else:
        pressure_divide = num_segments//(1/gradient_fraction)

    if pressure_divide > 0:
        pressure_change_incr = (pressure_range[1] - pressure_range[0]) / (pressure_divide)
    if pressure_divide == 0:
        import sys
        print('Segments are too large to create desired length of gradient section. Try make the segments shorter.')
        sys.exit()
    pressure = pressure_range[1]

    add_end = num_segments % (1/gradient_fraction)
    if add_end == 0:
        add_begin = 0
        add_end = 1
    else:
        add_begin = 1

    prev_pressure = 0
    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])

            '''PRESSURES'''
            valve_toggleOFF = '\n'
            valve_toggleON = '\n'
            if (i + 1) == 1:
                pressure = pressure_range[1]

            elif (i + 1) <= (num_segments // (1/gradient_fraction)) + add_begin:  # decreasing pressure for first 1/3 section
                pressure -= pressure_change_incr
                # valve_toggleOFF = valveOFF
                # valve_toggleON = valveON

            elif (i + 1) > (((1/gradient_fraction)-1) * (num_segments // (1/gradient_fraction))) + add_end:
                pressure += pressure_change_incr


            print(pressure)

            if prev_pressure > pressure:
                f.write(valveOFF)
                f.write(str('\n\r' + com[0] + '.write(' + str(setpress(pressure)) + ')'))
                f.write(valveON)


            else:
                f.write(str('\n\r' + com[0] + '.write(' + str(setpress(pressure)) + ')'))

            prev_pressure = pressure

            if (i+1) == num_segments or (i+1) == 1:
                f.write('\nG1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                f.write('\nG1 ' + input_variables[0] + str(sign * segment_len))



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

            valve_toggleOFF = '\n'
            valve_toggleON = '\n'
            if (i + 1) == 1:
                pressure = pressure_range[1]

            elif (i + 1) <= (num_segments // (1/gradient_fraction)) + add_begin:  # decreasing pressure for first 1/3 section
                pressure -= pressure_change_incr
                valve_toggleOFF = valveOFF
                valve_toggleON = valveON

            elif (i + 1) > (((1 / gradient_fraction) - 1) * (num_segments // (1 / gradient_fraction))) + add_end:
                pressure += pressure_change_incr

            print(pressure)

            f.write(valve_toggleOFF)
            f.write(str('\n\r' + com[0] + '.write(' + str(setpress(pressure)) + ')'))
            f.write(valve_toggleON)

            f.write('\nG1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    export_file_txt = 'triangle_gcode.txt'
    export_gradient_file_txt = 'triangle_grad_gcode.txt'
    outer_length_horizontal = 15
    inner_length_horizontal = 5
    fil_width = 0.8
    x_y_ratio = 15
    gradient_fraction = 1/5
    triangle_isos(export_file_txt, x_y_ratio, outer_length_horizontal, inner_length_horizontal, fil_width)
    #triangle_equi(export_file_txt, outer_length_horizontal, inner_length_horizontal, fil_width)

    gcode_list = open_gcode(export_file_txt)
    input_line_list = find_distances(gcode_list)

    segments = ['length', 1] # ['type', value], type options: 'length', 'number'

    pressure_range = [19,23]
    ### Pressure box and valve settings
    com = ["serialPort1"]
    valve = [6, 7]

    setpress_start = str('\n\r' + com[0] + '.write(' + str(setpress(pressure_range[1])) + ')')  # material 1

    toggleON = str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')')  # turn on material 2
    toggleOFF = toggleON

    valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve[0]) + ', True)'
    valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve[0]) + ', False)'

    with open(export_gradient_file_txt, "w") as f:
        f.write(setpress_start)
        f.write(toggleON)
        for i in range(len(input_line_list[0])):
            input_line = [input_line_list[0][i], input_line_list[1][i]]
            Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF)

        f.write(toggleOFF)
        f.write(valveOFF)

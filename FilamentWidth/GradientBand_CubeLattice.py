'''
Author: Sarah Propst
Date: 10/24/23

Can create rectangular structures with gradient central band
'''
# This function creates a gradient infill of a square lattice

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

    toggle = str("b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03'")
    return toggle
def Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF):
    ###
    input_variables_original = input_line[0]
    input_dist_original = input_line[1]
    input_dist = []
    input_variables = []
    for i in range(len(input_dist_original)):
        if input_dist_original[i] != 0:
            input_dist.append(input_dist_original[i])
            input_variables.append(input_variables_original[i])


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

    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])

            '''PRESSURES'''
            valve_toggleOFF = '\n'
            valve_toggleON = '\n'
            if (i + 1) == 1:
                pressure = pressure_range[1]

            elif (i + 1) <= (num_segments // (1/gradient_fraction)) + add_begin:
                pressure -= pressure_change_incr
                valve_toggleOFF = valveOFF
                valve_toggleON = valveON

            elif (i + 1) > (((1/gradient_fraction)-1) * (num_segments // (1/gradient_fraction))) + add_end:
                pressure += pressure_change_incr

            print('gradient segment pressure = ', pressure)

            f.write(valve_toggleOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
            f.write(valve_toggleON)

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

            print('gradient segment pressure = ', pressure)

            f.write(valve_toggleOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
            f.write(valve_toggleON)

            f.write('\nG1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))
def gradient_square_lattice(fil_spacing, xy_num_fil, num_layers, segment_length, fil_width, layer_height, pressure_range, valveON, valveOFF,):
    distance_list = []
    var_list = []
    x_num_fil = xy_num_fil[0]
    y_num_fil = xy_num_fil[1]
    for layer in range(num_layers):
        if (layer + 1)%2 != 0:
            num_filaments = y_num_fil
            length = ((x_num_fil-1)*fil_spacing)
        else:
            num_filaments = x_num_fil
            length = ((y_num_fil -1) * fil_spacing)

        pressure = pressure_range[1]
        for fil in range(num_filaments):
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
                Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF)

                if (fil + 1) != num_filaments:
                    distance_list.append([y_dist])
                    var_list.append(['Y'])
                    f.write('\nG1 Y' + str(y_dist))

            else:
                x_sign_even_row = x_sign_odd_row * -1 # reverses the x-direction
                if (fil+1)%2 != 0: # odd fil
                    y_sign_even_row = -y_sign_odd_row
                else:
                    y_sign_even_row = -y_sign_even_row

                x_dist = x_sign_even_row * fil_spacing
                y_dist = y_sign_even_row * length

                if num_filaments % (1 / gradient_fraction) == 0:
                    pressure_divide = num_filaments // (1 / gradient_fraction) - 1
                else:
                    pressure_divide = num_filaments // (1 / gradient_fraction)

                if pressure_divide > 0:
                    pressure_change_incr = (pressure_range[1] - pressure_range[0]) / (pressure_divide)

                if pressure_divide == 0:
                    import sys
                    print(
                        'num filaments too small create desired length of gradient section.')
                    sys.exit()


                add_end = num_filaments % (1 / gradient_fraction)
                if add_end == 0:
                    add_begin = 0
                    add_end = 1
                else:
                    add_begin = 1

                pressure_change = (pressure_range[1] - pressure_range[0])//(num_filaments*gradient_fraction)

                valve_toggleOFF = '\n'
                valve_toggleON = '\n'
                if (fil + 1) == 1:
                    pressure = pressure_range[1]

                elif (fil + 1) <= (num_filaments // (1 / gradient_fraction)) + add_begin:
                    pressure -= pressure_change_incr
                    valve_toggleOFF = valveOFF
                    valve_toggleON = valveON

                elif (fil + 1) > (((1 / gradient_fraction) - 1) * (num_filaments // (1 / gradient_fraction))) + add_end:
                    pressure += pressure_change_incr


                print(pressure)

                f.write(valve_toggleOFF)
                f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
                f.write(valve_toggleON)
                f.write('\nG1 Y' +str(y_dist))

                # distance_list.append([y_dist])
                # var_list.append(['Y'])
                if (fil + 1) != num_filaments:
                    distance_list.append([x_dist])
                    var_list.append(['X'])
                    f.write('\nG1 X' + str(x_dist))

        distance_list.append([layer_height])
        var_list.append(['Z'])

        f.write('\nG1 Z' +str(layer_height))



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ### File names
    export_file = '231027_GradientBand_B_ThickBand_NG_gcode.txt'
    save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

    ### Geometric Settings
    fil_spacing = 2
    segments = ['length', 1]  # for gradient
    gradient_fraction = 1/2
    xy_num_fil = [int(20 / fil_spacing),
                  int(20 / fil_spacing)]  # [x, y] or [lenght, width] number of filaments in these directions

    fil_width = 0.45
    layer_height = 0.55
    num_layers = int(20/layer_height)

    pressure_range = [25, 18]#[16, 24]  # [center of print, outside edge of print]
    NG_pressure = 22
    ### Pressure box and valve settings
    com = "serialPort1"
    valve = 6

    setpress_start = str('\n\r' + com + '.write(' + str(setpress(pressure_range[1])) + ')') # material 1
    toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
    toggleOFF = toggleON

    valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
    valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'

    com_NG = "serialPort2"
    setpress_NG = str('\n\r' + com_NG + '.write(' + str(setpress(NG_pressure) + ')'))  # material 1
    toggleON_NG = str('\n\r' + com_NG + '.write(' + str(togglepress()) + ')')  # turn on material 2
    toggleOFF_NG = toggleON_NG

    import os.path

    completeName = os.path.join(save_path, export_file)
    f = open(completeName, "w")
    f.write(setpress_start)
    f.write(setpress_NG)
    f.write(toggleON)
    f.write(valveON)



    gradient_square_lattice(fil_spacing, xy_num_fil, num_layers, segments, fil_width, layer_height, pressure_range, valveON, valveOFF, )

    f.write(valveOFF)
    f.write(toggleOFF)
    f.write(toggleOFF_NG)
    f.close()
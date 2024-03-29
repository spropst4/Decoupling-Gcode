'''
Author: Sarah Propst
Date: 9/7/23

Can create rectangular structures with square gradient infill
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
    import serial
    from codecs import encode
    from textwrap import wrap
    toggle = str("b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03'")
    return toggle
def Gradient_line_segmentation(input_line, segments, pressure_range, mid_point_pressure,valveON, valveOFF,):
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
        segment_len = line_length/num_segments
        first_n_last_segment_len = segment_len
    print('------num-segments', num_segments)
    if num_segments%2 != 0:
        odd_extra = segment_len
        even_extra = 0
    else:
        odd_extra = 0
        even_extra = 1


    pressure_incr = (pressure_range[1] - pressure_range[0]) / (num_segments//2 - even_extra)

    distance_count = 0
    pressure = pressure_range[1]

    valve_toggleOFF = '\n'
    valve_toggleON = '\n'
    pressure_list = []
    valve_list = []

    for i in range(num_segments):
        pressure_list.append(mid_point_pressure)
        valve_list.append(['\n', '\n'])

    pressure = pressure_range[1]
    # if pressure_incr <= 0:
    #     for i in range(num_segments):
    #         if i > 0:
    #             pressure -= pressure_incr
    #         if pressure <= mid_point_pressure:
    #             pressure_list[i] = pressure
    #             valve_list[i] = [valveOFF, valveON]
    #             pressure_list[-(i + 1)] = pressure
    #elif pressure_incr >= 0:

    if pressure_range[1] > pressure_range[0]:
        for i in range(num_segments):
            if i > 0:
                pressure -= pressure_incr
            if pressure >= mid_point_pressure:
                pressure_list[i] = pressure
                pressure_list[-(i + 1)] = pressure
            else:
                break
    elif pressure_range[1] < pressure_range[0]:
        for i in range(num_segments):
            if i > 0:
                pressure -= pressure_incr
            if pressure <= mid_point_pressure:
                pressure_list[i] = pressure
                pressure_list[-(i + 1)] = pressure
            else:
                break



    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])
            distance_count += segment_len

            pressure = round(pressure_list[i], 1)#round(pressure_list[i]*2)/2 # rounds to neares .5


            if i > 0 and pressure_list[i] == pressure_list[i-1]:
                f.write('\n')

            elif i > 0 and pressure_list[i] < pressure_list[i-1] - 0.2:# - 0.2:
                f.write(str(valveOFF))
                f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
                f.write(str(valveON))
                print('------toggling off/on')
                print('Pressure = ', pressure)



            elif i == 0 or pressure_list[i] >= pressure_list[i-1] - 0.2: # - 0.2:
                f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))

                print('Pressure = ', pressure)

            if (i+1) == num_segments or (i+1) == 1:
                f.write('\nG1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                f.write('\nG1 ' + input_variables[0] + str(sign * segment_len))

        #print(pressure_list)

###NOTE: in this code, I switched x and y in the outputed g-code so that I could print two samples side by side easier
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

        even_extra = 0
        odd_extra = 1
        if num_filaments % 2 == 0:
            even_extra = 1
            odd_extra = 0

        pressure_change_between_midpoints = (pressure_range[1] - pressure_range[0]) / (num_filaments // 2 - even_extra)

        for fil in range(num_filaments):
            print(';----new FIL', num_filaments)

            if (fil + 1) == 1:
                dist_from_center = (num_filaments // 2) - (even_extra)
                mid_point_pressure = pressure_range[1]
                pressure_gradient_region = 0

            elif (fil+ 1) <= (num_filaments//2) + odd_extra:
                dist_from_center -= 1
                mid_point_pressure -= pressure_change_between_midpoints
                pressure_gradient_region += fil_spacing

            elif (fil + 1) == num_filaments//2 + even_extra:
                dist_from_center = dist_from_center


            else:
                dist_from_center += 1
                mid_point_pressure += pressure_change_between_midpoints
                pressure_gradient_region -= fil_spacing


            #print(';-------------------mid point pressure', round(mid_point_pressure,2))
            pressure_range_filament = [mid_point_pressure, pressure_range[1]]

            segments = ['length', segment_length]
            #print('--------------------segment_length', segment_length)
            #print(';-------------------pressure_gradient_region', round(pressure_gradient_region, 2))

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


                input_line = [['Y'], [x_dist]]
                Gradient_line_segmentation(input_line, segments, pressure_range_filament, mid_point_pressure,valveON, valveOFF,)

                # distance_list.append([x_dist])
                # var_list.append(['X'])

                if (fil + 1) != num_filaments:
                    distance_list.append([y_dist])
                    var_list.append(['X'])
                    f.write('\nG1 X' + str(y_dist))

            else:
                x_sign_even_row = x_sign_odd_row * -1 # reverses the x-direction
                if (fil+1)%2 != 0: # odd fil
                    y_sign_even_row = -y_sign_odd_row
                else:
                    y_sign_even_row = -y_sign_even_row

                x_dist = x_sign_even_row * fil_spacing
                y_dist = y_sign_even_row * length


                input_line = [['X'], [y_dist]]
                Gradient_line_segmentation(input_line, segments, pressure_range_filament, mid_point_pressure,valveON, valveOFF,)

                # distance_list.append([y_dist])
                # var_list.append(['Y'])
                if (fil + 1) != num_filaments:
                    distance_list.append([x_dist])
                    var_list.append(['Y'])
                    f.write('\nG1 Y' + str(x_dist))

        distance_list.append([layer_height])
        var_list.append(['Z'])

        f.write('\nG1 Z' +str(layer_height))


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    ### File names
    ### File names
    export_file = '231027_GradientInfillV5_Rectangle_decreasing_gcode.txt'
    save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

    ### Geometric Settings
    fil_spacing = 2
    segment_length = 1  # for gradient
    xy_num_fil = [int(30 / fil_spacing),
                  int(30 / fil_spacing)]  # int(5 / fil_spacing)]#[int(140 / fil_spacing),4] #int(5 / fil_spacing)] #[int(30 / fil_spacing), int(30 / fil_spacing)]#[int(140 / fil_spacing),int(6 / fil_spacing)]  # [x, y] or [lenght, width] number of filaments in these directions

    fil_width = 0.75
    layer_height = 0.55 #0.45  # 0.45
    num_layers = int(15 / layer_height)

    pressure_range = [20, 30]  # [38, 46]#[45, 37]  # [center of print, outside edge of print]
    pressure_noGrad = 25  # np.average(pressure_range) + 3

    ### Pressure box and valve settings
    com = 'serialPort1'
    com_noGrad = 'serialPort2'
    valve = 6 #6
    valve_noGrad = 7#7

    # Gradient
    setpress_start = str('\n\r' + com + '.write(' + str(setpress(pressure_range[1])) + ')') # material 1
    toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
    toggleOFF = toggleON

    valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
    valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'

    # No Gradient
    setpress_start_noGrad = str('\n\r' + com_noGrad + '.write(' + str(setpress(pressure_noGrad)) + ')')  # material 1
    toggleON_noGrad = str('\n\r' + com_noGrad + '.write(' + str(togglepress()) + ')')  # turn on material 2
    toggleOFF_noGrad = toggleON_noGrad

    valveON_noGrad = '\n{aux_command}WAGO_ValveCommands(' + str(valve_noGrad) + ', True)'
    valveOFF_noGrad = '\n{aux_command}WAGO_ValveCommands(' + str(valve_noGrad) + ', False)'

    import os.path

    completeName = os.path.join(save_path, export_file)
    f = open(completeName, "w")
    f.write(setpress_start)
    f.write(setpress_start_noGrad)

    f.write(toggleON)
    f.write(toggleON_noGrad)

    f.write(valveON)
    f.write(valveON_noGrad)

    f.write('\nG1 Y5')
    gradient_square_lattice(fil_spacing, xy_num_fil, num_layers, segment_length, fil_width, layer_height, pressure_range, valveON, valveOFF,)

    f.write(valveOFF)
    f.write(valveOFF_noGrad)

    f.write(toggleOFF)
    f.write(toggleOFF_noGrad)

    f.close()

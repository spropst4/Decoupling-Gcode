'''
Author: Sarah Propst
Date: 8/29/23

This function creates a diamond lattice structure composed of a zig-zag print path.
Gradient thickness towards the nodes.
1/2 1/2 - decr incr
'''
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
import numpy as np

def generate_diamond_lattice(num_rows, num_zig_units, len_zig, corner_width):
    x_zig = len_zig[0]
    y_zig = len_zig[1]
    distance_list = []
    for rows in range(num_rows):
        for zig_units in range(num_zig_units):
            if (rows+1)%2 != 0: #odd rows
                if (zig_units+1)%2 !=0: # odd zig
                    distance_list.append([x_zig, y_zig])
                else:
                    distance_list.append([x_zig, -y_zig])
            else: # even rows
                if (zig_units+1)%2 !=0: # odd zig
                    if (zig_units+1) == 1 or (zig_units+1) == num_zig_units: # this sections limits overlap at the peaks of the diamonds
                        slope = len_zig[1] / len_zig[0]
                        x_lengthen_for_fil = corner_width / (2 * np.sqrt(1 + slope ** 2))
                        y_lengthen_for_fil = slope * x_lengthen_for_fil
                        distance_list.append([-(x_zig), y_zig + y_lengthen_for_fil])
                    else:
                        distance_list.append([-x_zig, y_zig])
                else:
                    distance_list.append([-x_zig, -y_zig])

    for rows in range(num_rows):
        if (rows + 1) % 2 != 0:  # odd rows
            if (rows + 1) == 1:
                slope = len_zig[1] / len_zig[0]
                x_lengthen_for_fil = corner_width / (2 * np.sqrt(1 + slope ** 2))
                y_lengthen_for_fil = slope * x_lengthen_for_fil
                distance_list.append([-(x_zig + 0.5*x_lengthen_for_fil), -(y_zig + y_lengthen_for_fil)])

            else:
                distance_list.append([-(x_zig), -(y_zig + y_lengthen_for_fil)])
                print('---here', x_zig )
        else:
            if (rows + 1) == num_rows:
                distance_list.append([(x_zig + 0.5*x_lengthen_for_fil), -(y_zig + y_lengthen_for_fil)])
            else:
                distance_list.append([(x_zig), -(y_zig + y_lengthen_for_fil)])

    for elem in distance_list:
        print('G1 X' + str(elem[0]) + ' Y' + str(elem[1]))

    return distance_list, x_lengthen_for_fil
def Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF):
    print('-------------------')
    ###
    input_variables = ['X', 'Y'] #input_line[0]
    input_dist_original = input_line
    input_dist = []
    for elem in input_dist_original:
        if elem != 0:
            input_dist.append(elem)


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


### File names
export_file = '230922_Gradient_diamond_lattice_V2Path_gcode.txt'
export_file_NOGRADIENT = '230921_NO_Gradient_diamond_lattice_V2Path_gcode.txt'
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

Z_var = 'D'

### Geometric Settings
plates = [False,2] # [do you want to have solid plates printed at top and bottom?, if so, how many rows? (must be an even number)]
num_rows = 6 # must be even
num_zig_units = 5 # number of diagonals per row (use odd number)
len_zig = [5, 5] # [x, y]
corner_width = 1 #0.8 # 0.8 # controls the distance between where the corners of the zig zag meet
filament_width = 0.75

gradient_fraction = 1/2 # how much of the filament is a gradient
segments = ['length', 0.5] # ['type', value], type options: 'length', 'number'
pressure_range = [44, 59] # [center of strut, nodes]
pressure_NG = 52 #pressure_range[1]
pressure_plate = 52

z_height = .45
num_layers = int(10/z_height) #round(0.5*((num_rows*len_zig[0])/z_height)) #37


### Pressure box and valve settings
com = ["serialPort2", "serialPort1"]
valve = [7,6]

setpress_start = str('\n\r' + com[0] + '.write(' + str(setpress(pressure_range[1])) + ')') # material 1
setpress_noGradient = str('\n\r' + com[1] + '.write(' + str(setpress(pressure_NG) + ')')) # material 1
plate_press = str('\n\r' + com[0] + '.write(' + str(setpress(pressure_plate) + ')')) # material 1

toggleON = str('\n\r'+com[0] +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

toggleON_NG = str('\n\r'+com[1] +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF_NG = toggleON_NG

valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve[0]) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve[0]) + ', False)'
valveON_NG = '\n{aux_command}WAGO_ValveCommands(' + str(valve[1]) + ', True)'
valveOFF_NG = '\n{aux_command}WAGO_ValveCommands(' + str(valve[1]) + ', False)'

input_line_list = generate_diamond_lattice(num_rows, num_zig_units, len_zig,corner_width)
reverse_line_list = input_line_list[::-1]


lattice_generate = generate_diamond_lattice(num_rows, num_zig_units, len_zig, corner_width)
input_line_list = lattice_generate[0]
x_lengthen_for_fil = lattice_generate[1]

import os.path
completeName = os.path.join(save_path, export_file)
f = open(completeName, "w")
f.write(setpress_start)
f.write(setpress_noGradient)

f.write(toggleON)
f.write(toggleON_NG)

f.write(valveON)
f.write(valveON_NG)

f.write('\nG1 X5')
for layer in range(num_layers):

    ## This section adds the plates at bottom of print
    if (layer + 1) % 2 == 0 and plates[0] == True:
        f.write(valveOFF)
        f.write(plate_press)
        f.write(valveON)

        #f.write('\nG1 X' + str(x_lengthen_for_fil))
        for repeat_plate in range(plates[1]):
            f.write('\nG1 Y' + str(-filament_width))

            if (repeat_plate + 1) % 2 != 0: # odd
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units - 1)))
            else:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units - 1)))
        f.write('\nG1 Z' + str(z_height))
        for repeat_plate in range(plates[1]):


            if (repeat_plate + 1) % 2 == 0 or plates[1] == 1:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units - 1)))
            else:
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units - 1)))

            f.write('\nG1 Y' + str(filament_width))


    for i in range(len(input_line_list)):
        input_line = input_line_list[i]
        Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF)

        ### This section adds the plates at top of print
        if (layer + 1)%2 == 0 and (i+1) == (num_rows * num_zig_units) - (num_zig_units - 1) and plates[0] == True: # even layers only
            f.write(valveOFF)
            f.write(plate_press)
            f.write(valveON)
            f.write('\nG1 Z' + str(-z_height))
            for repeat_plate in range(plates[1]):
                f.write('\nG1 Y' + str(filament_width))
                if (repeat_plate+1)%2 != 0: # odd
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units - 1)))
                else:
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units - 1)))
            f.write('\nG1 Z' + str(z_height))
            for repeat_plate in range(plates[1]):

                if (repeat_plate+1)%2 == 0 or plates[1] == 1:# even
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units - 1)))
                else:
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units - 1)))

                f.write('\nG1 Y' + str(-filament_width))

    # if (layer+1) != num_layers and (layer+1)%2 != 0:
    #     f.write('\nG1 Z'+str(z_height))
    print(layer+1)
    if ((layer+1) != num_layers and (layer+1)%2 == 0 and plates[0] == True) or (plates[0] == False and (layer+1) != num_layers) :
        #f.write('\nG1 X' + str(x_lengthen_for_fil)+' Z'+str(z_height))
        f.write('\nG1 Z' + str(z_height))

#f.write('\nG1 X-5')
f.write(valveOFF)
f.write(valveOFF_NG)

f.write(toggleOFF)
f.write(toggleOFF_NG)

f.close()

############################NO GRADIENT########################

import os.path
completeName = os.path.join(save_path, export_file_NOGRADIENT)
f = open(completeName, "w")
f.write(setpress_noGradient)
f.write(toggleON)
f.write(valveON)

f.write('\nG1 X5')
for layer in range(num_layers):

    ## This section adds the plates at bottom of print
    if (layer + 1) % 2 == 0 and plates[0] == True:

        #f.write('\nG1 X' + str(x_lengthen_for_fil))
        for repeat_plate in range(plates[1]):
            f.write('\nG1 Y' + str(-filament_width))

            if (repeat_plate + 1) % 2 != 0: # odd
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units - 1)))
            else:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units - 1)))
        f.write('\nG1 ' + Z_var + str(z_height))
        for repeat_plate in range(plates[1]):
            if (repeat_plate + 1) % 2 == 0 or plates[1] == 1:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units - 1)))
            else:
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units - 1)))

            f.write('\nG1 Y' + str(filament_width))


    for i in range(len(input_line_list)):
        input_line = input_line_list[i]
        f.write('\nG1 X' + str(input_line[0]) + ' Y' + str(input_line[1]))

        ### This section adds the plates at top of print
        if (layer + 1)%2 == 0 and (i+1) == (num_rows * num_zig_units) - (num_zig_units - 1) and plates[0] == True: # even layers only

            f.write('\nG1 ' + Z_var + str(-z_height))
            for repeat_plate in range(plates[1]):
                f.write('\nG1 Y' + str(filament_width))
                if (repeat_plate+1)%2 != 0: # odd
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units - 1)))
                else:
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units - 1)))
            f.write('\nG1 ' + Z_var + str(z_height))
            for repeat_plate in range(plates[1]):

                if (repeat_plate+1)%2 == 0 or plates[1] == 1:# even
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units - 1)))
                else:
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units - 1)))

                f.write('\nG1 Y' + str(-filament_width))


    if ((layer+1) != num_layers and (layer+1)%2 == 0 and plates[0] == True) or (plates[0] == False and (layer+1) != num_layers) :
        #f.write('\nG1 X' + str(x_lengthen_for_fil)+' Z'+str(z_height))
        f.write('\nG1 ' + Z_var + str(z_height))

#f.write('\nG1 X-5')
f.write(valveOFF)
f.write(toggleOFF)

f.close()




'''
Author: Sarah Propst
Date: 8/29/23

This function creates a diamond lattice structure composed of a zig-zag print path.
Gradient thickness towards the nodes.

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
                    if (zig_units + 1) == 1 and (rows +1) > 1:  # this sections limits overlap at the peaks of the diamonds
                        slope = len_zig[1] / len_zig[0]
                        x_lengthen_for_fil = corner_width / (2 * np.sqrt(1 + slope ** 2))
                        y_lengthen_for_fil = slope * x_lengthen_for_fil
                        distance_list.append([(x_zig), y_zig + corner_width])
                    else:
                        distance_list.append([x_zig, y_zig])
                else:
                    distance_list.append([x_zig, -y_zig])

                if (zig_units + 1) == num_zig_units:
                    distance_list.append([0, 2*y_zig + corner_width])

            else: # even rows
                if (zig_units+1)%2 !=0: # odd zig

                    distance_list.append([-x_zig, -y_zig])
                else:
                    distance_list.append([-x_zig, y_zig])
    distance_to_add_plate = len(distance_list)
    for row in range(num_rows):
        if (row+1)%2 != 0: # odd points
            if (row+1) == 1:
                distance_list.append([0, -2*(y_zig) - corner_width])
            else:
                distance_list.append([0, -2*(y_zig + corner_width)])


    for elem in distance_list:
        print('G1 X' + str(elem[0]) + ' Y' + str(elem[1]))
    return distance_list, distance_to_add_plate
def Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF):
    #print('-------------------')
    ###
    input_variables_original = ['X', 'Y'] #input_line[0]
    input_dist_original = input_line
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

            elif (i + 1) <= (num_segments // (1/gradient_fraction)) + add_begin:  # decreasing pressure for first 1/3 section
                pressure -= pressure_change_incr
                valve_toggleOFF = valveOFF
                valve_toggleON = valveON

            elif (i + 1) > (((1/gradient_fraction)-1) * (num_segments // (1/gradient_fraction))) + add_end:
                pressure += pressure_change_incr

            print(pressure)

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

            print(pressure)

            f.write(valve_toggleOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
            f.write(valve_toggleON)

            f.write('\nG1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))


### File names
export_file = '230908_Gradient_diamond_lattice_V3Path_forNOGRADIENT_gcode.txt'
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

### Geometric Settings
plates = [True, 2] # [do you want to have solid plates printed at top and bottom?, if so, how many rows? (must be an even number)]
num_rows = 6 #use even number
num_zig_units = 6 # number of diagonals per row (use even number)
len_zig = [5, 5] # [x, y]
corner_width = 0#0.3 # controls the distance between where the corners of the zig zag meet
filament_width = 0.55

gradient_fraction = 1/2 # i.e. what fraction of filament is decreasing? Must be  <= 1/2
segments = ['length', .5] # ['type', value], type options: 'length', 'number'
pressure_range = [40, 55] # [center of strut, nodes]
z_height = .5
num_layers = round(10/z_height)#round((num_zig_units*len_zig[0])/z_height)#37
print(num_layers)

### Pressure box and valve settings
com = "serialPort1"
valve = 6

setpress_start = str('\n\r' + com + '.write(' + str(setpress(pressure_range[1])) + ')') # material 1
plate_press = str('\n\r' + com + '.write(' + str(setpress(np.average(pressure_range)) + ')')) # material 1
toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'

diamond_lattice_output = generate_diamond_lattice(num_rows, num_zig_units, len_zig, corner_width)

input_line_list = diamond_lattice_output[0]
reverse_line_list = input_line_list[::-1]
distance_to_add_top_plate = diamond_lattice_output[1]
import os.path
completeName = os.path.join(save_path, export_file)
f = open(completeName, "w")
f.write(setpress_start)
f.write(toggleON)
f.write(valveON)

f.write('\nG1 X10')
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
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units)))
            else:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units)))
        f.write('\nG1 Z' + str(z_height))
        for repeat_plate in range(plates[1]):

            if (repeat_plate + 1) % 2 == 0  or plates[1] == 1:
                f.write('\nG1 X' + str(-len_zig[0] * (num_zig_units )))
            else:
                f.write('\nG1 X' + str(len_zig[0] * (num_zig_units)))

            f.write('\nG1 Y' + str(filament_width))


    for i in range(len(input_line_list)):
        input_line = input_line_list[i]
        Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF)

        ### This section adds the plates at top of print
        if (layer + 1)%2 == 0 and (i+1) == (distance_to_add_top_plate) and plates[0] == True: # even layers only
            f.write(valveOFF)
            f.write(plate_press)
            f.write(valveON)
            f.write('\nG1 Z' + str(-z_height))
            for repeat_plate in range(plates[1]):
                f.write('\nG1 Y' + str(filament_width))
                if (repeat_plate+1)%2 != 0: # odd
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units)))
                else:
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units)))
            f.write('\nG1 Z' + str(z_height))
            for repeat_plate in range(plates[1]):

                if (repeat_plate+1)%2 == 0  or plates[1] == 1:# even
                    f.write('\nG1 X' + str(-len_zig[0]*(num_zig_units)))
                else:
                    f.write('\nG1 X' + str(len_zig[0]*(num_zig_units)))

                f.write('\nG1 Y' + str(-filament_width))

    # if (layer+1) != num_layers and (layer+1)%2 != 0:
    #     f.write('\nG1 Z'+str(z_height))

    if ( (layer+1) != num_layers and (layer+1)%2 == 0 and plates[0]==True) or (plates[0] == False and (layer+1) != num_layers) :
        #f.write('\nG1 X' + str(x_lengthen_for_fil)+' Z'+str(z_height))
        f.write('\nG1 Z' + str(z_height))


f.write(valveOFF)
f.write(toggleOFF)
f.write('\nG1 X-5')
f.close()

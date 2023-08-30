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

def generate_lattice(num_lines, line_spacing, num_layers):
    total_length = (num_lines-1)*line_spacing
    segments = num_lines - 1
    segment_length = total_length/segments

    var_list = []
    distance_list = []

    for layers in range(num_layers):
        for lines in range(num_lines):
            for seg in range(segments):
                if (layers+1)%2 != 0:  #odd layers
                    if (lines+1)%2 != 0: # odd lines and odd layers
                        distance_list.append([segment_length]
                        var_list.append(['X'])

                        distance_list.append([segment_length])
                        var_list.append(['Y'])
                    else:  # even lines and odd layers
                        distance_list.append([-segment_length]
                        var_list.append(['X'])

                        distance_list.append([segment_length])
                        var_list.append(['Y'])
                else:
                    if (lines + 1) % 2 != 0:  # odd lines and odd layers
                        distance_list.append([-segment_length]
                        var_list.append(['Y'])

                        distance_list.append([-segment_length])
                        var_list.append(['X'])

                    else:  # even lines and odd layers
                        distance_list.append([segment_length]
                        var_list.append(['Y'])

                        distance_list.append([-segment_length])
                        var_list.append(['X'])




    return distance_list

def Gradient_line_segmentation(input_line, segments, pressure_range, save_path, export_file, valveON, valveOFF, setpress_start, toggleON, toggleOFF):

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

    if num_segments%2 == 0:
        pressure_divide = num_segments//3 - 1
    else:
        pressure_divide = num_segments//3

    pressure_change_incr = (pressure_range[1] - pressure_range[0]) / (pressure_divide)
    pressure = pressure_range[1]

    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])

            '''PRESSURES'''
            valve_toggleOFF = '\n'
            valve_toggleON = '\n'
            if 1 < (i + 1) <= num_segments // 3 + 1:  # decreasing pressure for first segment
                pressure -= pressure_change_incr
                valve_toggleOFF = valveOFF
                valve_toggleON = valveON

            elif (i + 1) < (2*num_segments // 3) + 1:
                pressure = pressure


            else:
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

            '''PRESSURES'''
            valve_toggleOFF = '\n'
            valve_toggleON = '\n'
            if 1 < (i + 1) <= num_segments // 3 +1:  # decreasing pressure for first segment
                pressure -= pressure_change_incr
                valve_toggleOFF = valveOFF
                valve_toggleON = valveON

            elif (i + 1) < 2 * num_segments // 3 + 1:
                pressure = pressure


            else:
                pressure += pressure_change_incr

            print(pressure)

            f.write(valve_toggleOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
            f.write(valve_toggleON)

            f.write('\nG1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))


### File names
export_file = '230829_Gradient_diamond_lattice_gcode.txt'
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

### Geometric Settings
num_lines =
line_spacing =
num_layers =
segments = ['length', .5] # ['type', value], type options: 'length', 'number'
pressure_range = [21, 42]

### Pressure box and valve settings
com = "serialPort1"
valve = 1

setpress_start = str('\n\r' + com + '.write(' + str(setpress(pressure_range[1])) + ')') # material 1
toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'


input_line_list = generate_diamond_lattice(num_rows, num_zig_units, len_zig,filament_width)
import os.path
completeName = os.path.join(save_path, export_file)
f = open(completeName, "w")
f.write(setpress_start)
f.write(toggleON)
f.write(valveON)

for i in range(len(input_line_list)):
    input_line = input_line_list[i]
    Gradient_line_segmentation(input_line, segments, pressure_range, save_path, export_file, valveON, valveOFF, setpress_start, toggleON, toggleOFF)

f.write(valveOFF)
f.write(toggleOFF)
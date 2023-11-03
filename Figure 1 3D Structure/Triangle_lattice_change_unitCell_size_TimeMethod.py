import numpy as np

################# For pressure box commands
def setpress(pressure):
    # IMPORTS
    from codecs import encode
    from textwrap import wrap


    pressure = round(pressure, 1)

    pressure = str(pressure * 10)
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
    format_command = '\\x' + format_command
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
def grayscale_value_2_pressure_ratio(grayscale_value, pressure):
    full_pressure_white = pressure[1][0]
    least_pressure_white = pressure[1][1]

    fraction_white = grayscale_value/255  # if closer to 1, value is closer to white
    pressure_white = (full_pressure_white-least_pressure_white)*fraction_white + least_pressure_white

    print('-------------------')
    pressure_black = (full_pressure_white+least_pressure_white) - pressure_white


    return [pressure_black, pressure_white]

def pressurebox_str_command(com, pressure):
    return str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')')
def pressurebox_toggle_str_command(com):
    return str('\n\r' + com + '.write(' + str(togglepress()) + ')')

def valve_str_command(valve, command):
    return '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', ' +str(command) + ')'

################# For updating size of unit cell
def find_distances(myline, ch1, ch2, hex_side_length, direction, offset):
    if ch1 in myline or ch2 in myline:
        list = myline.split(" ")
        distance1 = 0
        distance2 = 0
        offset_list = []
        for elem in list:

            if ch1 in elem :
                distance1 = elem.strip(ch1)
                distance1 = float(distance1) / float(5)
                distance1 = direction * distance1 * hex_side_length

            if ch2 in elem:
                distance2 = elem.strip(ch2)
                distance2 = float(distance2) / float(5)
                distance2 = direction * distance2 * hex_side_length

            if '{offset}' in elem or '{offset_x}' in elem or '{offset_y}' in elem:
                offset_update = float(elem.replace('{offset}', str(offset)).replace('{offset_x}', str(offset/np.sqrt(5))).replace('{offset_y}', str(offset*2/np.sqrt(5))))
                offset_list.append(direction * offset_update)

            else:
                offset_list.append(0)

        while len(offset_list) < 5:
            offset_list.append(0)

        offset1 = offset_list[2]
        offset2 = offset_list[4]
        return list[0] + ' ' + ch1 + str(distance1 + offset1) + ' ' + ch2 + str(distance2 + offset2)

    else:
        return myline
def open_and_edit_gcode(gcode_txt, toggle_ON_list, toggle_OFF_list, hex_side_length, offset, filament_width, gap_size, visualize):
    gcode_list = []
    gcode_list_reverse = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            myline = myline.strip('\n')
            #myline = myline.replace('G0', 'G1')
            #myline = myline.removeprefix('G1 ').removeprefix('G0 ')
            myline = myline.replace("'Material 1 ON", toggle_ON_list[0]).replace("'Material 2 ON", toggle_ON_list[1]).replace("'Material 1 OFF", toggle_OFF_list[0]).replace("'Material 2 OFF", toggle_OFF_list[1])
            update_xy_distances = find_distances(myline, 'X', 'Y', hex_side_length, 1, offset)
            reverse_xy_direction = find_distances(myline, 'X', 'Y', hex_side_length, -1, offset)

            myline = update_xy_distances
            myline_reverse = reverse_xy_direction

            if visualize == False:
                myline = myline.replace('G0', 'G1')
                myline_reverse = myline_reverse.replace('G0', 'G1')



            myline = myline.replace('{gap}', 'G1 Y'+str(gap_size))
            myline_reverse = myline_reverse.replace('{gap}', 'G1 Y-' + str(gap_size))

            gcode_list.append(myline)
            gcode_list_reverse.append(myline_reverse)


        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        gcode_list_reverse = [x for x in gcode_list_reverse if x != ""]  # removes spaces



        gcode.close()
        return gcode_list, gcode_list_reverse

################# For writing and exporting gcode
def write_and_export_gcode(export_gcode_txt, gcode_list_1repeat_unit, gcode_list_Section1_Only, Z_var,setpress_list, valveON_list, valveOFF_list):
    odd_layers_1repeat_unit = gcode_list_1repeat_unit[0]
    even_layers_1repeat_unit = gcode_list_1repeat_unit[1]

    odd_layers_Section1_Only = gcode_list_Section1_Only[0]
    even_layers_Section1_Only = gcode_list_Section1_Only[1]



    f.write(valveON_list[0])

    for repeat in range(3):
        f.write("\nG1 X3")
        f.write(valveON_list[1])
        f.write(valveOFF_list[0])
        f.write("\nG1 X3")
        f.write(valveON_list[0])
        f.write(valveOFF_list[1])


    f.write('\nG1 X' + str(3))

    for layer in range(num_layers):
        #f.write("\n'layer " + str(layer + 1))

        if (layer + 1) % 2 != 0:
            for repeat in range(number_of_repeat_units):
                for elem in odd_layers_1repeat_unit:
                    f.write('\n' + elem)

            for elem in odd_layers_Section1_Only:
                f.write('\n' + elem)

        else:
            for repeat in range(number_of_repeat_units):
                for elem in even_layers_1repeat_unit:
                    f.write('\n' + elem)
            for elem in even_layers_Section1_Only:
                f.write('\n' + elem)

        f.write('\nG1 ' + Z_var + str(layer_height))

    f.write(valveOFF_list[0])

######################################### Import/Export
gcode_txt_1RepeatUnit = 'Triangle_lattice_honeycomb_1RepeatUnit_noOffset_V3.txt'
gcode_txt_Section1_Only = 'Triangle_lattice_honeycomb_Section1_Only_noOffset_gap.txt'
export_gcode_txt = '231011_Triangle_lattice_honeycomb_gcode.txt'
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

visualize = False

######################################### Geometric variables
hex_side_length = 7
number_of_repeat_units = 2
num_layers = 3
layer_height = 1
filament_width = 1

gap_size = 0.5*filament_width # this leaves a small space between each row so that they don't overlap and smear

offset = 0
Z_var = 'Z'
######################################### Pressure Box Settings
pressure = [34, 34]
com = ['serialPort1', 'serialPort2']
valve = [6, 7]

######################################## Pressure Box Commands
setpress_list = []
valve_ON_list = []
valve_OFF_list = []
toggleON_list = []
for i in range(len(com)):
    setpress_list.append(pressurebox_str_command(com[i], pressure[i]))
    valve_ON_list.append(valve_str_command(valve[i], True))
    valve_OFF_list.append(valve_str_command(valve[i], False))
    toggleON_list.append(pressurebox_toggle_str_command(com[i]))

toggleOFF_list = toggleON_list
######################################## Write G-Code
gcode_list_1repeat_unit = open_and_edit_gcode(gcode_txt_1RepeatUnit, valve_ON_list, valve_OFF_list, hex_side_length,
                                              offset, filament_width, gap_size, visualize)
gcode_list_Section1_Only = open_and_edit_gcode(gcode_txt_Section1_Only, valve_ON_list, valve_OFF_list,
                                               hex_side_length, offset, filament_width, gap_size, visualize)

###################################### Export G-Code

import os.path

completeName = os.path.join(save_path, export_gcode_txt)
f = open(completeName, 'w')

for i in range(len(setpress_list)):
    f.write(setpress_list[i])
    f.write(toggleON_list[i])

export = write_and_export_gcode(export_gcode_txt, gcode_list_1repeat_unit, gcode_list_Section1_Only, Z_var,setpress_list, valve_ON_list, valve_OFF_list)

for elem in valve_OFF_list:
    f.write(elem)


for elem in toggleOFF_list:
    f.write(elem)


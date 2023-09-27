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

def Gradient_line_segmentation(input_line, segments, pressure_increments, pressure):
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
            pressure += pressure_increments
            print(pressure)
            if pressure_increments <0:
                f.write(valveOFF)
                f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))
                f.write(valveON)
            else:
                f.write(str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')'))

            if (i+1) == num_segments or (i+1) == 1:
                f.write('\nG1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                f.write('\nG1 ' + input_variables[0] + str(sign * segment_len))

    print('------')




##INPUTS#############################################################################################################
export_file = "230927_Generate_Gradient_ImprovedCorners_gcode.txt"
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

shape = 'square' # options: 'line test' or 'square'

# Desired XYZ motion
side_length = 30
accel_region = 1
corner_pressure_psi = 20
print_pressure_psi = 30
segments = ['length', 0.5]
if accel_region > 0:
    pressure_increments = (print_pressure_psi - corner_pressure_psi)/(accel_region/segments[1])
######################################################################################################################
com = "serialPort1"
valve = 7

corner_pressure = str('\n\r' + com + '.write(' + str(setpress(corner_pressure_psi)) + ')') # material 1
print_pressure = str('\n\r' + com + '.write(' + str(setpress(print_pressure_psi)) + ')') # material 1
toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'

######
import os.path
completeName = os.path.join(save_path, export_file)

with open(completeName, "w") as f:
    f.write(corner_pressure)
    #f.write(print_pressure)
    f.write(toggleON)
    f.write(valveON)
    f.write('\nG1 Y5')

    if shape == 'square':
        for i in range(4):
            if i == 0:
                gcode = '\nG1 Y'
                var = 'Y'
                sign = 1
            if i == 1:
                gcode = '\nG1 X'
                var = 'X'
                sign = 1
            if i == 2:
                gcode = '\nG1 Y-'
                var = 'Y'
                sign = -1
            if i == 3:
                gcode = '\nG1 X-'
                var = 'X'
                sign = -1

            f.write(corner_pressure)

            Gradient_line_segmentation([[var], [sign*accel_region]], segments, pressure_increments, corner_pressure_psi)

            f.write(print_pressure)
            f.write(gcode + str(side_length - 2 * accel_region))

            Gradient_line_segmentation([[var], [sign*accel_region]], segments, -pressure_increments, print_pressure_psi)

    f .write(toggleOFF)
    f.write(valveOFF)



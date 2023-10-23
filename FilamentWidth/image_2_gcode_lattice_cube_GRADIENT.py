import cv2
import numpy as np

def setpress(pressure):
    # IMPORTS
    from codecs import encode
    from textwrap import wrap

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

        #input_line_list.append(result_dist_list)
        #input_var_list.append(result_var_list)

    return result_var_list, result_dist_list
def Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON, valveOFF):
    gcode_list = []
    print('-------------------')
    ###
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

    valve_toggleOFF = '\n'
    valve_toggleON = '\n'
    pressure_list = []
    valve_list = []
    for i in range(num_segments):
        pressure_list.append(pressure_range[0])
        valve_list.append([valve_toggleOFF, valve_toggleON])

    prev_pressure = 0
    if len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])

            '''PRESSURES'''

            if (i + 1) == 1:
                pressure_list[i] = pressure_range[1]
                pressure = pressure_range[1]

            elif (i + 1) <= (num_segments // (1/gradient_fraction)) + add_begin:  #
                pressure -= pressure_change_incr
                pressure_list[i] = pressure
                valve_list[i] = [valveOFF, valveON]

                # valve_toggleOFF = valveOFF
                # valve_toggleON = valveON

            elif (i + 1) > (((1/gradient_fraction)-1) * (num_segments // (1/gradient_fraction))) + add_end:
                pressure += pressure_change_incr
                pressure_list[i] = pressure

            pressure = round(pressure_list[i], 2)
            gcode_list.append(str(valve_list[i][0]))
            gcode_list.append(str('\n\r' + com[0] + '.write(' + str(setpress(pressure)) + ')'))
            gcode_list.append(str(valve_list[i][1]))
            print('Pressure = ', pressure)

            if (i + 1) == num_segments or (i + 1) == 1:
                gcode_list.append('\nG1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                gcode_list.append('\nG1 ' + input_variables[0] + str(sign * segment_len))

    return gcode_list


'''Lattice print prints a lattice structure'''
def image_2_gcode_CheckerboardCube_latticeprint(image_name, fil_width,layer_height, num_layers,gradient_fraction, color_list,setpress_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, export_txt_file, save_path):
    if gcode_simulate == True:
        gcode_color1 = "G0 "
    else:
        gcode_color1 = "G1 "

    img = cv2.imread(image_name, 0)

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []
    var_list = []
    dist_list = []
    command_list = []
    first_toggle_ON = True

    layer_count = 0

    first_image = img
    second_image = cv2.flip(img, 1)
    second_image = cv2.rotate(second_image, cv2.ROTATE_90_CLOCKWISE)

    first_image_ON = True

    short_move_sign = 1
    dist_sign = 1

    for layers in range(img.shape[0]):
        print('layers = ', layers)
        if (layers + 1) % 2 == 0:  # even layers
            current_image = second_image
            long_move_sign = -1*short_move_sign
            short_move_sign = -1*dist_sign

            long_dist_var = 'Y'
            short_dist_var = 'X'

        else:  # odd layers:
            current_image = first_image
            long_move_sign = -1*short_move_sign
            short_move_sign = -1*dist_sign

            long_dist_var = 'X'
            short_dist_var = 'Y'


        layer_count += 1

        for i in range(len(current_image)):  # number of rows of pixels  (image height)
            current_image_row = current_image[i]

            if (i + 1) % 2 == 0:  # even rows:
                current_image_row = np.flip(current_image_row)  # reverse order of pixel
                dist_sign = -1*long_move_sign  # reverse of print

            else:  # odd rows:
                dist_sign = 1*long_move_sign

            first_pix = True
            for j in range(len(current_image_row)):  # number of pixels in a row (image width)
                pixel = current_image_row[j]

                if prev_pixel != pixel:
                    for k in range(len(color_list)):
                        color = color_list[k]

                        if pixel == color:
                            color_ON = color_ON_list[k]
                            color_OFF = color_OFF_list[k]

                    if dist != 0:
                        if pixel == color_list[1]:
                            if first_pix == True:
                                dist = dist - (0.5*fil_width)
                                first_pix = False
                            gcode_list.append(gcode + long_dist_var + str(dist_sign*dist) )

                        if pixel == color_list[0]:
                            if first_pix == True:
                                dist = dist - (0.5*fil_width)
                                first_pix = False
                            gcode_line = [gcode + ' ' + long_dist_var + str(dist_sign*dist)]
                            input_line = find_distances(gcode_line)
                            gcode_segmented_output = Gradient_line_segmentation(input_line, gradient_fraction, segments, pressure_range, valveON,valveOFF)
                            gcode_list_segmented = gcode_segmented_output
                            for line in gcode_list_segmented:
                                gcode_list.append(line)

                    # if first_toggle_ON == False:
                    #     gcode_list.append(color_ON)
                    # else:
                    #     gcode_list.append(color_ON)
                    #     first_toggle_ON = False

                    dist = 0

                    gcode = 'G1 '
                    if pixel == gcode_simulate_color:
                        gcode = gcode_color1


                dist += fil_width

                prev_pixel = pixel
                prev_color_OFF = color_OFF

            dist = dist - (0.5*fil_width)
            if first_pix == True:
                dist = dist - (0.5*fil_width)
            if pixel == color_list[0]:
                gcode_list.append(gcode + ' ' + long_dist_var + str(dist_sign * dist))

            else:
                gcode_line = [gcode + ' ' + long_dist_var + str(dist_sign * dist)]
                input_line = find_distances(gcode_line)
                gcode_segmented_output = Gradient_line_segmentation(input_line,gradient_fraction, segments, pressure_range, valveON, valveOFF)
                gcode_list_segmented = gcode_segmented_output
                for line in gcode_list_segmented:
                    gcode_list.append(line)

            if (i+1) != len(img):
                gcode_list.append(gcode + ' ' + short_dist_var + str(short_move_sign * fil_width))

            else:
                gcode_list.append(gcode + ' ' + 'Z' + str(layer_height))



            dist = 0




    import os.path
    completeName = os.path.join(save_path, export_txt_file)

    f = open(completeName, 'w')
    f.write('\n\rG91')
    for elem in setpress_list:
        f.write(elem)
    f.write(str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')') ) # turn on material 2)
    f.write(valveON)
    f.write('\nG1 X-5')
    for i in range(len(gcode_list)):
        f.write('\n\r' + str(gcode_list[i]))


    f.write(str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')') ) # turn on material 2)
    f.write(valveOFF)
# Grayscale:
black = 0
white = 255


############################################ Define variables ##################################

image_name = '231022_25x25_SmileyTest_V2.png'
export_txt_file = '231022_25x25_SmileyTest_V2_gcode.txt'
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'
fil_width = 1.5  # width of filament/nozzle
layer_height = 0.45
num_layers = 10
gradient_fraction = 1/3
segments = ['length', 0.3] # ['type', value], type options: 'length', 'number'

# Number of ports used
com = ["serialPort1"]

# Define the Pressures
pressure_range = [19, 28]
valve = 6

############################################ Define colors ##################################
color1 = black
color2 = white

color_list = [black, white]

gcode_simulate = False  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1

############################################ Create command lists ##################################
valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'
setpress_list = []
color_ON_list = []
color_OFF_list = []

for i in range(len(pressure_range)):
    setpress_list.append(str('\n\r' + com[0] + '.write(' + str(setpress(pressure_range[1])) + ')'))
    color_ON_list.append('\n\r' + com[0] + '.write(' + str(setpress(pressure_range[i])) + ')')
    color_OFF_list.append('\n')



####################################################################### LATTICE PRINT ######################################################################
output = image_2_gcode_CheckerboardCube_latticeprint(image_name, fil_width, layer_height, num_layers, gradient_fraction,
                                                     color_list, setpress_list, color_ON_list, color_OFF_list,
                                                     gcode_simulate, gcode_simulate_color, export_txt_file, save_path)


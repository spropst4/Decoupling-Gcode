"""
9/4/23 - Sarah Propst
Purpose: convert image to gcode print path with a gradient background

NOTES:
    -Use a 2-toned image
        -Background (or white) will be the gradient
    -Gradient will start with a high ratio of Material 1 and end with a low ratio of Material
    -Gradient_segments should always be in 'length' setting
    -Try to only use segment lengths the easily divide into the dimensions of the image and y_dist
    -Gradient_pressure_range shows the starting ranges of the two materials
        -[Material2, Material1]
        -Material 1 > Material 2
        -Values will be reversed by the end of the print




"""
import cv2
import numpy as np

### To set pressures
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

### To convert rgb colors to hex
def rgb_to_hex(b, g, r):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)


### To segment lines and create gradient
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
def Gradient_line_segmentation(input_line, segments, pressure1, pressure2, pressure_incr):
    gcode_list = []
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

    if num_segments == 0: # moves shorter than the segmentation
        gcode_list.append('G1 ' + input_variables[0] + str(input_dist[0]))
    elif num_segments == 1 and first_n_last_segment_len < line_length:
        gcode_list.append('G1 ' + input_variables[0] + str(input_dist[0]))

    elif len(input_dist) == 1: # horizontal or vertical lines
        for i in range(num_segments):
            sign = input_dist[0] / abs(input_dist[0])
            pressure1 -= pressure_incr
            pressure2 += pressure_incr
            gcode_list.append('Pressure 1: ' + str(pressure1) + '; Pressure 2: ' + str(pressure2))
            if (i+1) == num_segments or (i+1) == 1:
                gcode_list.append('G1 ' + input_variables[0] + str(sign * first_n_last_segment_len))
            else:
                gcode_list.append('G1 ' + input_variables[0] + str(sign * segment_len))

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

            pressure1 -= pressure_incr
            pressure2 += pressure_incr
            gcode_list.append('Pressure 1: ' + str(pressure1) + '; Pressure 2: ' + str(pressure2))
            gcode_list.append('G1 ' + input_variables[0] + str(a_sign*a_segment) + ' ' + input_variables[1] + str(b_sign*b_segment))

    return gcode_list, pressure1, pressure2

### To create gcode image
def image_2_gcode_2plusMaterials(image_name, y_dist, gradient_pressure_range, gradient_segments, offset, color_list, other_color_50_50_split, other_color,color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, color_code):

    pressure1 = gradient_pressure_range[1]  #material 1 gradient starts at 100% or higher ratio
    pressure2 = gradient_pressure_range[0] #material 2 gradient starts at 0% or lower ratio
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    if color_code == 'HEX':
        img = cv2.imread(image_name)

    elif color_code == 'RGB':
        img = cv2.imread(image_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif color_code == 'Grayscale':
        img = cv2.imread(image_name, 0)

    img = cv2.flip(img, 1) # this makes sure the image is not backwards
    cv2.imwrite('CheckImage.png', img)

    img_shape = img.shape
    img_height = img_shape[0]  # height
    img_width = img_shape[1]  # width

    num_pressure_changes_total = (img_height*img_width + img_height)/gradient_segments[1]
    pressure_incr = (pressure1 - pressure2) / (num_pressure_changes_total-1)

    pressure1 += pressure_incr # this makes sure that starting values are correct
    pressure2 -=pressure_incr # this makes sure that starting values are correct

    dist = 0
    prev_pixel = ''
    prev_color_OFF = ''
    color_OFF = ''
    gcode = ''
    gcode_list = []

    for i in range(len(img)):  # number of rows of pixels  (image height)
        current_image = img[i]
        if color_code == 'HEX':
            raw_current_image = img[i]
            current_image = []
            for elem in raw_current_image:
                pixel = elem
                pixel = rgb_to_hex(pixel[0], pixel[1], pixel[2])
                current_image.append(pixel)

        if i != len(img) - 1: # will be used in the offset
            next_image = img[i+1]
            if color_code == 'HEX':
                raw_next_image = img[i+1]
                next_image = []
                for elem in raw_next_image:
                    pixel = elem
                    pixel = rgb_to_hex(pixel[0], pixel[1], pixel[2])
                    next_image.append(pixel)

        if (i + 1) % 2 == 0:  # even rows:
            current_image = np.flip(current_image)  # reverse order of pixel
            dist_sign = '-'  # reverse x-direction of print

        else:  # odd rows:
            next_image = np.flip(next_image)
            dist_sign = ''

        if i > 0:
            current_image = current_image[offset:]

        next_image = next_image[0:offset]

        pixels_to_print = np.concatenate((current_image, next_image), axis=0) #np.append(current_image, next_image)

        if i == len(img) - 1:
            pixels_to_print = current_image

        for pix in range(len(pixels_to_print)):  # number of pixels in a row (image width)
            pixel = pixels_to_print[pix]


            if pixel not in color_list:
                if other_color_50_50_split == True and color_code == 'Grayscale':  # True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
                    diff_pixel = []
                    for color in range(len(color_list)):

                        diff_pixel.append(abs(pixel - color))

                    pixel = np.min(diff_pixel)

                else:
                    pixel = other_color

            if prev_pixel != pixel:
                for col in range(len(color_list)):
                    color = color_list[col]

                    if pixel == color:
                        color_ON = color_ON_list[col]
                        color_OFF = color_OFF_list[col]

                if dist != 0:
                    gcode_line = [gcode + dist_sign + str(dist)]
                    input_line = find_distances(gcode_line)
                    gcode_segmented_output = Gradient_line_segmentation(input_line, gradient_segments, pressure1, pressure2, pressure_incr)

                    gcode_list_segmented = gcode_segmented_output[0]
                    for line in gcode_list_segmented:
                        gcode_list.append(line)

                    pressure1 = gcode_segmented_output[1]
                    pressure2 = gcode_segmented_output[2]

                    # gcode_list.append(gcode + dist_sign + str(dist))
                gcode_list.append(color_ON)

                if i > 0 or pix > 0:
                    gcode_list.append(prev_color_OFF)

                dist = 0

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1


            dist += y_dist

            prev_pixel = pixel
            prev_color_OFF = color_OFF

        gcode_line = [gcode + dist_sign + str(dist)]
        input_line = find_distances(gcode_line)
        gcode_segmented_output = Gradient_line_segmentation(input_line, gradient_segments, pressure1, pressure2, pressure_incr)
        gcode_list_segmented = gcode_segmented_output[0]
        for line in gcode_list_segmented:
            gcode_list.append(line)

        pressure1 = gcode_segmented_output[1]
        pressure2 = gcode_segmented_output[2]

        #gcode_list.append(gcode + dist_sign + str(dist))

        if i == len(img)-1:
            gcode_list.append(prev_color_OFF)

            if offset > 0:
                gcode_line = [gcode + dist_sign + str(offset)]
                input_line = find_distances(gcode_line)
                gcode_segmented_output = Gradient_line_segmentation(input_line, gradient_segments, pressure1, pressure2,
                                                                    pressure_incr)
                gcode_list_segmented = gcode_segmented_output[0]
                for line in gcode_list_segmented:
                    gcode_list.append(line)

                pressure1 = gcode_segmented_output[1]
                pressure2 = gcode_segmented_output[2]

                #gcode_list.append(gcode + dist_sign + str(offset))

        gcode_line = ['G1 Y' + str(y_dist)]
        input_line = find_distances(gcode_line)
        gcode_segmented_output = Gradient_line_segmentation(input_line, gradient_segments, pressure1, pressure2,
                                                            pressure_incr)
        gcode_list_segmented = gcode_segmented_output[0]
        for line in gcode_list_segmented:
            gcode_list.append(line)

        pressure1 = gcode_segmented_output[1]
        pressure2 = gcode_segmented_output[2]

        #gcode_list.append('G1 Y' + str(y_dist))
        dist = 0


    return gcode_list

############################################### 2+ Colors function ################################
image_name = 'Missouri.png'
gcode_export = 'Missouri_gcode.txt'

img = cv2.imread(image_name)
pix_hex_list = []

### Geometry
y_dist = 1  # width of filament/nozzle
offset = 0
gradient_segments = ['length', 1]
gradient_pressure_range = [15, 30] # [Material2, Material1], Material1 > Material2

### Ports and valves
com = ["serialPort1", "serialPort2"]#, 'serialPort3']
valve = [6,7]
pressure = [23, 23]# #, 26]

### Color
color_code = 'Grayscale' #RGB' # 'HEX', 'Grayscale'
if color_code == 'HEX':
    ## HEX:
    black = '#000000'
    white = '#ffffff'
    blue = '#68ace5'
elif color_code == 'RGB':
    black = [0, 0, 0]
    white = [255, 255, 255]
    blue = [104, 172, 229]
else:
    ## Grayscale:
    black = 0
    white = 255
    blue = 150

color1 = black
color2 = white
color3 = blue

color_list = [color1, color2]

# what color do you want pixels that aren't black or white?
other_color_50_50_split = False  # ONly works in grayscale mode; True: pixel becomes color that it is closest to; False: pixel color is chosen as you specify below
other_color = white

### Simulate Image
gcode_simulate = False  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = color1


setpress_list = []
color_ON_list = []
color_OFF_list = []
pressure_box_ON_list = []
pressure_box_OFF_list = []
for i in range(len(com)):
    setpress_list.append(str('\n\r' + com[i] + '.write(' + str(setpress(pressure[i])) + ')'))

    color_ON_list.append('\n{aux_command}WAGO_ValveCommands(' + str(valve[i]) + ', True)')
    color_OFF_list.append('\n{aux_command}WAGO_ValveCommands(' + str(valve[i]) + ', False)')

    pressure_box_ON_list.append(str('\n\r' + com[i] + '.write(' + str(togglepress()) + ')'))
    pressure_box_OFF_list.append(str('\n\r' + com[i] + '.write(' + str(togglepress()) + ')'))



############################################ Executes ##################################
gcode_list = image_2_gcode_2plusMaterials(image_name, y_dist, gradient_pressure_range, gradient_segments, offset,
                                          color_list, other_color_50_50_split, other_color, color_ON_list,
                                          color_OFF_list, gcode_simulate, gcode_simulate_color, color_code)



with open(gcode_export,'w') as f:
    for i in range(len(setpress_list)):
        f.write('\n' +setpress_list[i])

        f.write('\n' + pressure_box_ON_list[i])

    f.write('\nG91\r')
    f.write('\nG1 X10')
    for elem in gcode_list:
        f.write(elem + '\n')

    f.write('\n' + pressure_box_ON_list[i])


f.close()

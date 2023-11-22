"""
9/4/23 - Sarah Propst
Purpose: convert image to gcode print path (use valves for toggling)

"""
import cv2
import numpy as np
import os

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

def pressurebox_setpress_str_command(port, pressure, start):
    if start == True:
        insert = '{preset}'
    else:
        insert = ''
    return str('\n\r'+insert+ port + '.write(' + str(setpress(pressure)) + ')')

def pressurebox_toggle_str_command(port, start):
    if start == True:
        insert = '{preset}'
    else:
        insert = ''
    return str('\n\r' +insert+ port + '.write(' + str(togglepress()) + ')')

def valve_str_command(valve, command):
    return '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', ' +str(command) + ')'

def rgb_to_hex(b, g, r):
    return '#{:02x}{:02x}{:02x}'.format(r, g, b)

def image_2_gcode_latticeprint(image_list, fil_width,layer_height, color_list,setpress_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, off_color, export_txt_file):
    if gcode_simulate == True:
        gcode_color1 = "G0 "
    else:
        gcode_color1 = "G1 "

    img_list = []
    for i in range(len(image_list)):
        image = path + '\\' + image_list[i]
        if color_code == 'HEX':
            img = cv2.imread(image)

        elif color_code == 'RGB':
            img = cv2.imread(image)
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

        elif color_code == 'Grayscale':
            img = cv2.imread(image, 0)

        if (i + 1) % 2 == 0:  # even layers/images
            img = cv2.flip(img, 1)  # rotates image
            img = cv2.rotate(img, cv2.ROTATE_90_CLOCKWISE)

        img_list.append(img)

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

    first_image_ON = True

    short_move_sign = 1
    dist_sign = 1
    first_ON = False
    for layers in range(len(img_list)):
        current_image = img_list[layers]
        print('layers = ', layers)
        if (layers + 1) % 2 == 0:  # even layers
            long_move_sign = -1*short_move_sign
            short_move_sign = -1*dist_sign

            long_dist_var = 'Y'
            short_dist_var = 'X'

        else:  # odd layers:
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

                        if pixel == off_color:
                            color_ON = color_OFF_list
                            color_OFF = ''

                    if first_ON == False :
                        print(True)
                        gcode_list.append(color_ON)
                        gcode_list.append('\nG1 X-5')
                        first_ON = True

                    if dist != 0:
                        if first_pix == True:
                            dist = dist - (0.5*fil_width)
                            first_pix = False

                            if pixel != off_color:
                                gcode_list.append(color_ON)

                        gcode_list.append(gcode + long_dist_var + str(dist_sign*dist))
                        if pixel == off_color:
                            for elem in color_ON:
                                gcode_list.append(elem)
                        else:
                            gcode_list.append(prev_color_OFF)
                            gcode_list.append(color_ON)

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

            gcode_list.append(gcode + ' ' + long_dist_var + str(dist_sign * dist))

            if (i+1) != len(img):
                gcode_list.append(gcode + ' ' + short_dist_var + str(short_move_sign * fil_width))

            else:
                gcode_list.append(gcode + ' ' + 'Z' + str(layer_height))

            dist = 0


    f = open(export_txt_file, 'w')
    f.write('\n\rG91')
    for elem in setpress_list:
        f.write(elem)
    for elem in pressure_box_ON_list:
        f.write(elem)
    for i in range(len(gcode_list)):
        f.write('\n\r' + str(gcode_list[i]))
    for elem in color_OFF_list:
        f.write(elem)

############################################### 2+ Colors function ################################
path = 'C:\\Users\\sprop\\PycharmProjects\\pythonProject\\Img2gcode_3D\\'
folder = 'HalfSphereTest'

gcode_export = path + folder + '_gcode.txt'

path = path+folder
image_list = os.listdir(path)
print(image_list)
y_dist = 1  # width of filament/nozzle
z_height = 1
offset = 0

color_code = 'Grayscale' #RGB' # 'HEX', 'Grayscale'

com = ["serialPort1", "serialPort2"]#, 'serialPort3']
valve = [6,7]
pressure = [23, 23]# #, 26]

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

color1 = black # OFF
color2 = white
color3 = blue

color_list = [color1, color2]

off_color = black

gcode_simulate = True  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = off_color

setpress_list = []
color_ON_list = []
color_OFF_list = []
pressure_box_ON_list = []
pressure_box_OFF_list = []
for i in range(len(com)):
    setpress_list.append(pressurebox_setpress_str_command(com[i], pressure[i], True))

    color_ON_list.append(valve_str_command(valve[i], 1))
    color_OFF_list.append(valve_str_command(valve[i], 0))

    pressure_box_ON_list.append(pressurebox_toggle_str_command(com[i], True))
    pressure_box_OFF_list.append(pressurebox_toggle_str_command(com[i], True))

############################################ Executes ##################################
image_2_gcode_latticeprint(image_list, y_dist, z_height, color_list,setpress_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, off_color, gcode_export)

"""
9/4/23 - Sarah Propst
Purpose: convert image to gcode print path (use valves for toggling)

"""
import cv2
import numpy as np

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
    full_pressure_bl = pressure[0][0]
    least_pressure_bl = pressure[0][1]

    fraction_white = grayscale_value/255  # if closer to 1, value is closer to white
    pressure_white = (full_pressure_white-least_pressure_white)*fraction_white + least_pressure_white

    # pressure_white += least_pressure_white
    #
    # pressure_black = (full_pressure_bl+least_pressure_bl)*(1-fraction_white)
    # pressure_black += least_pressure_bl

    print('-------------------')
    pressure_black = (full_pressure_white+least_pressure_white) - pressure_white

    #print([pressure_black, pressure_white])

    return [pressure_black, pressure_white]

def pressurebox_str_command(com, pressure):
    return str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')')
def pressurebox_toggle_str_command(com):
    return str('\n\r' + com + '.write(' + str(togglepress()) + ')')

def valve_str_command(valve, command):
    return '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', ' +str(command) + ')'

def image_2_gcode_2ColorGradient(image_name, y_dist, offset, pressure, com_list_gradient, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, color_code):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    if color_code == 'RGB':
        img = cv2.imread(image_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif color_code == 'Grayscale':
        img = cv2.imread(image_name, 0)



    img = cv2.flip(img, 1) # this makes sure the image is not backwards
    cv2.imwrite('CheckImage.png', img)

    dist = 0
    prev_pixel = img[0][0]

    prev_pressures = grayscale_value_2_pressure_ratio(prev_pixel, pressure)


    gcode = 'G1 X'
    gcode_list = []
    for press in range(len(prev_pressures)):
        pressure_val = round(prev_pressures[press], 1)
        com_val = com_list_gradient[press]
        gcode_list.append(pressurebox_str_command(com_val, pressure_val))# + ' ;Pressure = '+str(pressure_val))
        #print(com_val, pressure_val)

    for elem in color_ON_list:
        gcode_list.append(elem)
    gcode_list.append('G1 X10')
    for i in range(len(img)):  # number of rows of pixels  (image height)
        current_image = img[i]

        if i != len(img) - 1: # will be used in the offset
            next_image = img[i+1]

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

            pressure_values = grayscale_value_2_pressure_ratio(pixel, pressure)
            print(pixel, pressure_values)

            if prev_pixel != pixel:
                if dist != 0:
                    gcode_list.append(gcode + dist_sign + str(dist))

                for press in range(len(pressure_values)):
                    pressure_val = round(pressure_values[press],1)
                    com_val = com_list_gradient[press]
                    #gcode_list.append(pressurebox_str_command(com_val, pressure_val))
                    if pressure_val < prev_pressures[press]:
                        gcode_list.append(color_OFF_list[press])
                        gcode_list.append(pressurebox_str_command(com_val, pressure_val)) #+ ' ;Pressure = ' + str(pressure_val))
                        gcode_list.append(color_ON_list[press])
                    else:
                        gcode_list.append(pressurebox_str_command(com_val, pressure_val)) #+ ' ;Pressure = ' + str(pressure_val))
                    print(com_val, pressure_val)
                dist = 0

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1


            dist += y_dist

            prev_pixel = pixel
            prev_pressures = pressure_values

        gcode_list.append(gcode + dist_sign + str(dist))
        if i == len(img)-1:
            gcode_list.append(gcode + dist_sign + str(offset))

        gcode_list.append('G1 Y' + str(y_dist))
        dist = 0


    return gcode_list


def image_2_gcode_2ColorGradient_wSolidImg(image_name, y_dist, offset, com_list_gradient, color_list_solid, com_solid_list, color_ON_list, color_OFF_list, gcode_simulate, gcode_simulate_color, color_code):
    if gcode_simulate == True:
        gcode_color1 = "G0 X"
    else:
        gcode_color1 = "G1 X"

    if color_code == 'RGB':
        img = cv2.imread(image_name)
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    elif color_code == 'Grayscale':
        img = cv2.imread(image_name, 0)



    img = cv2.flip(img, 1) # this makes sure the image is not backwards
    cv2.imwrite('CheckImage.png', img)

    dist = 0
    prev_pixel = img[0][0]

    prev_pressures = grayscale_value_2_pressure_ratio(prev_pixel, pressure)


    gcode = 'G1 X'
    gcode_list = []
    for press in range(len(prev_pressures)):
        pressure_val = prev_pressures[press]
        com_val = com_list_gradient[press]
        gcode_list.append(pressurebox_str_command(com_val, pressure_val) + ' ;Pressure = '+str(pressure_val))




    gcode_list.append('G1 X10')
    for i in range(len(img)):  # number of rows of pixels  (image height)
        current_image = img[i]

        if i != len(img) - 1: # will be used in the offset
            next_image = img[i+1]

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

            pressure_values = grayscale_value_2_pressure_ratio(pixel, pressure)
            #print(pixel, pressure_values)

            if prev_pixel != pixel:
                if dist != 0:
                    gcode_list.append(gcode + dist_sign + str(dist))

                if pixel not in color_list_solid:
                    if solid_color_ON[0] == True:

                        com = solid_color_ON[1]
                        gcode_list.append(pressurebox_toggle_str_command(com_solid_list[com]) + ' ;solid color off here')
                        solid_color_ON = [False, com]

                    for press in range(len(pressure_values)):
                        pressure_val = pressure_values[press]
                        com_val = com_list_gradient[press]
                        if pressure_val < prev_pressures[press]:
                            gcode_list.append(color_OFF_list[press])
                            gcode_list.append(pressurebox_str_command(com_val, pressure_val) + ' ;Pressure = ' + str(pressure_val))
                            gcode_list.append(color_ON_list[press])
                        else:
                            gcode_list.append(pressurebox_str_command(com_val, pressure_val) + ' ;Pressure = ' + str(pressure_val))
                    for elem in color_ON_list:
                        gcode_list.append(elem)
                else:
                    for i in range(len(color_list_solid)):
                        if pixel == color_list_solid[i]:
                            break
                    gcode_list.append(pressurebox_toggle_str_command(com_solid_list[i]) + ' ;solid color on here' )
                    for elem in color_OFF_list:
                        gcode_list.append(elem)

                    solid_color_ON = [True, i]
                    pressure_values = [0,0]

                dist = 0

                gcode = 'G1 X'
                if pixel == gcode_simulate_color:
                    gcode = gcode_color1

                prev_pixel = pixel
                prev_pressures = pressure_values

            dist += y_dist



        gcode_list.append(gcode + dist_sign + str(dist))
        if i == len(img)-1:
            gcode_list.append(gcode + dist_sign + str(offset))

        gcode_list.append('G1 Y' + str(y_dist))
        dist = 0


    return gcode_list

############################################### 2+ Colors function ################################
image_name = '230911_GradientPixelDiamond_50x50.png'#'230911_GradientPixelDiamond_50x50.png'
gcode_export = image_name.replace('.png', '_gcode.txt')
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

OnlyGradient = True # True if there is not a solid black image also in the print (like for the sunset)

y_dist = 1  # width of filament/nozzle
offset = 0

com_gradient_black = "serialPort1"
com_gradient_white = "serialPort2"
com_solid = "serialPort3"

valve_gradient_black = 6
valve_gradient_white = 7

pressure_gradient_black = [27, 16]   # [100% value, 0% value]
pressure_gradient_white = [27, 16]   # [100% value, 0% value]
#pressure_solid = 23

color_code = 'Grayscale' # 'Grayscale', 'RGB'
if color_code == 'RGB':
    black = [0, 0, 0]
    white = [255, 255, 255]
    blue = [104, 172, 229]
if color_code == 'Grayscale':
    ## Grayscale:
    black = 0
    white = 255

gradient_color1 = black
gradient_color2 = white
solid_color1 = black

color_list = [gradient_color1, gradient_color2]
com_list_gradient = [com_gradient_black, com_gradient_white]
valve = [valve_gradient_black, valve_gradient_white]
pressure = [pressure_gradient_black, pressure_gradient_white]

color_list_solid = [solid_color1]
com_solid_list = [com_solid]

gcode_simulate = False  # If True: writes black (color1) pixels as 'G0' moves
gcode_simulate_color = gradient_color1

setpress_list = []
color_ON_list = []
color_OFF_list = []
pressure_box_ON_list = []
pressure_box_OFF_list = []
for i in range(len(com_list_gradient)):
    setpress_list.append(pressurebox_str_command(com_list_gradient[i], pressure[i][1]))


    color_ON_list.append(valve_str_command(valve[i], True))
    color_OFF_list.append(valve_str_command(valve[i], False))

    pressure_box_ON_list.append(pressurebox_toggle_str_command(com_list_gradient[i]))
    pressure_box_OFF_list.append(pressurebox_toggle_str_command(com_list_gradient[i]))



############################################ Executes ##################################

if OnlyGradient == True:
    gcode_list = image_2_gcode_2ColorGradient(image_name, y_dist, offset, pressure, com_list_gradient, color_ON_list,color_OFF_list, gcode_simulate, gcode_simulate_color, color_code)
else:
    gcode_list = image_2_gcode_2ColorGradient_wSolidImg(image_name, y_dist, offset, com_list_gradient,color_list_solid, com_solid_list, color_ON_list,color_OFF_list, gcode_simulate, gcode_simulate_color,color_code)
import os.path
completeName = os.path.join(save_path, gcode_export)

with open(completeName,'w') as f:
    for i in range(len(setpress_list)):
        #f.write('\n' + setpress_list[i])

        f.write(pressure_box_ON_list[i])

    #f.write('\nG91\r')

    for elem in gcode_list:
        f.write('\n'+elem )

    f.write(pressure_box_ON_list[i])

    for elem in pressure_box_OFF_list:
        f.write(elem)

f.close()



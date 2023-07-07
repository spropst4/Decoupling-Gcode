import numpy as np
def generateCircle(num_sections_per_quarter, r_start, r_final,r_inner_solid, filament_width, export_gcode_txt, setpress_list, toggle_ON, toggle_OFF):
    color_flag_ON = 1
    with open(export_gcode_txt, 'w') as f:
        f.write('\n\rG91')

        for elem in setpress_list:
            f.write(elem)


        theta_between_moves = (np.pi / 2) / num_sections_per_quarter
        r = r_start
        color_start = toggle_ON[0]
        color_flag_ON = 0

        f.write(color_start)
        theta_for_ij = 0

        while r < r_inner_solid:
            i = round(-r * np.cos(theta_for_ij), 10)
            j = round(-r * np.sin(theta_for_ij), 10)



            f.write('\n\rG3 X0 Y0 I' + str(i) + ' J' + str(j))
            f.write(str('\n\r' + com[color_flag_ON] + '.write(' + str(setpress(pressure[color_flag_ON] - 2)) + ')'))  # material 1)
            f.write('\n\rG1 X' + str(filament_width))
            f.write(str('\n\r' + com[color_flag_ON] + '.write(' + str( setpress(pressure[color_flag_ON])) + ')'))  # material 1)
            r += filament_width

        while r <= r_final:
            theta_for_ij = 0
            theta_for_xy = theta_between_moves

            x_prev = r
            y_prev = 0
            for c in range(num_sections_per_quarter*4):
                x = round(r*np.cos(theta_for_xy), 10)
                y = round(r * np.sin(theta_for_xy),10)

                x_rel = x - x_prev
                y_rel = y - y_prev

                x_prev = x
                y_prev = y

                i = round(-r*np.cos(theta_for_ij),10)
                j = round(-r*np.sin(theta_for_ij),10)

                theta_for_ij += theta_between_moves
                theta_for_xy += theta_between_moves

                f.write('\n\rG3 X'+ str(x_rel) + ' Y' + str(y_rel) + ' I' + str(i) +  ' J'+ str(j))

                if color_flag_ON == 0: # odd segments
                    f.write(toggle_ON[1])
                    f.write(toggle_OFF[0])
                    color_flag_ON = 1
                else:  # odd segments
                    f.write(toggle_ON[0])
                    f.write(toggle_OFF[1])
                    color_flag_ON = 0


            r += filament_width
            #f.write(toggle_OFF[color_flag_ON])
            f.write(str('\n\r' + com[color_flag_ON] + '.write(' + str(setpress(pressure[color_flag_ON] - 1)) + ')'))  # material 1)
            f.write('\n\rG1 X'+ str(filament_width))
            f.write(str('\n\r' + com[color_flag_ON] + '.write(' + str(setpress(pressure[color_flag_ON])) + ')')) # material 1)
            #f.write(toggle_ON[color_flag_ON])

        if color_flag_ON == 0:  # odd segments
            f.write(toggle_OFF[0])
        else:
            f.write(toggle_OFF[1])

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

num_sections_per_quarter = 5
export_gcode_txt = '1DGC_GenerateCircle_divided_'+str(num_sections_per_quarter*4)+'_gcode.txt'


r_start = 0.5
r_final = 15
r_inner_solid = 1

filament_width = 1
pressure = [24, 24]

###############################################################################################################
com = ["serialPort1", "serialPort2"]
setpress1 = str('\n\r' + com[0] + '.write(' + str(setpress(pressure[0])) + ')') # material 1
setpress2 = str('\n\r' + com[1] + '.write(' + str(setpress(pressure[1])) + ')') # material 2

toggleON_1 = str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')') # turn on material 1
toggleOFF_1 = toggleON_1

toggleON_2 = str('\n\r' + com[1] + '.write(' + str(togglepress()) + ')')  #start 2nd material
toggleOFF_2 = toggleON_2 #'\n'  # "\nM792 ;SEND Ultimus_IO["+str(comRight)+"]= 0" #stop 2nd material

setpress_list = [setpress1, setpress2]
toggle_ON = [toggleON_1, toggleON_2]
toggle_OFF = [toggleOFF_1, toggleOFF_2]



###############################################################################################################
generateCircle(num_sections_per_quarter, r_start, r_final,r_inner_solid, filament_width, export_gcode_txt, setpress_list, toggle_ON,
               toggle_OFF)


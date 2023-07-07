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
def triangle2M(export_file_txt, outer_length,inner_length, setpress_list, toggle_ON, toggle_OFF):
    with open(export_file_txt, "w") as f:
        length = outer_length
        x = length/2
        y = np.sqrt(length**2 - x**2)
        f.write('\n\rG91')

        for elem in setpress_list:
            f.write(elem)

        f.write(toggle_ON[0])
        color_flag_ON = 0


        f.write('\n\rG1 X' + str(x) + ' Y' + str(y))
        f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))
        length -= 1
        f.write('\n\rG1 X' + str(-length))

        f.write(toggle_ON[1])
        f.write(toggle_OFF[0])
        color_flag_ON = 1

        slope = y/x
        count = 0
        while length > inner_length:
            x = (length-1)/2
            y = x*slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(y))

            x -= 0.5
            y = x * slope
            f.write('\n\rG1 X' + str(x) + ' Y' + str(-y))

            length -= 3

            f.write('\n\rG1 X' + str(-length))
            count += 1

            if count == 1:
                if color_flag_ON == 0:  # odd segments
                    f.write(toggle_ON[1])
                    f.write(toggle_OFF[0])
                    color_flag_ON = 1


                else:  # odd segments
                    f.write(toggle_ON[0])
                    f.write(toggle_OFF[1])
                    color_flag_ON = 0

                count = 0


        f.write(toggle_OFF[color_flag_ON])

outer_length = 30
inner_length = 1
export_file_txt = 'SimpleShapes_Triangle_2Materials_gcode.txt'

pressure = [28, 28]

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

triangle2M(export_file_txt, outer_length, inner_length, setpress_list, toggle_ON, toggle_OFF)









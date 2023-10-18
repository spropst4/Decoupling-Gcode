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

def pressurebox_str_command(port, pressure):
    return str('\n\r' + port + '.write(' + str(setpress(pressure)) + ')')
def pressurebox_toggle_str_command(com):
    return str('\n\r' + com + '.write(' + str(togglepress()) + ')')

def valve_str_command(valve, command):
    return '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', ' +str(command) + ')'


def generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type):
    #arc_length = r*theta_between_moves
    theta_between_moves = section_arc_length/r
    num_sections = (2*np.pi*circle_fraction)/theta_between_moves
    num_sections = round(num_sections)
    theta_between_moves = (2*np.pi*circle_fraction)/num_sections


    print('updated to section arc length so that num_sections is a whole number: ', (r*theta_between_moves))

    #theta_between_moves = (np.pi / (circle_fraction/2)) / num_sections
    pressure = start_settings[-1]
    f.write(pressurebox_str_command('serialPort1', pressure))
    print(pressure)
    if start_settings[0] == 'initial':
        sign = 1
        x_prev = r
        y_prev = 0
        theta_for_ij = 0
        theta_for_xy = theta_between_moves


    if start_settings[0] == 'update' and pattern_type == 'spiral':
        x_output = start_settings[1]
        if x_output < 0:
            sign = -1
        else:
            sign = 1
        x_prev = r
        y_prev = 0
        theta_for_ij = 0
        theta_for_xy = theta_between_moves


    elif start_settings[0] == 'update' and pattern_type == 'not spiral':
        x_prev = start_settings[2]
        y_prev = start_settings[3]
        theta_for_xy = start_settings[4]
        theta_for_ij = start_settings[5]
        sign = 1

    for c in range(num_sections):
        pressure += 0.2
        print(pressure)
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


        f.write('\n\rG3 X'+ str(sign*x_rel) + ' Y' + str(sign*y_rel) + ' I' + str(sign*i) + ' J'+ str(sign*j))
        f.write(pressurebox_str_command('serialPort1', pressure))


    return ['update', sign*x_rel, x_prev, y_prev, theta_for_xy, theta_for_ij, pressure]



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    export_file = '231018_GradientCircle_gcode.txt'
    save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

    r = 3
    section_arc_length = 1
    circle_fraction = 1/2
    start_pressure = 15
    start_settings = ['initial', start_pressure]

    import os.path

    completeName = os.path.join(save_path, export_file)
    f = open(completeName, "w")
    '''
    spiral pattern
    - pattern_type = 'spiral'
    - can do increasing and decreasing spirals
    '''
    pattern_type = 'spiral'  # options: 'spiral', 'not spiral'
    start_settings = generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type)

    count = 0.8
    while r <= 20:
        section_arc_length += 0.5
        #print('---', start_settings)
        r += count
        start_settings = generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type)

        count = count * 1.2
    '''
    full circle from circle fractions
    - consecutive loops must use some section arc length
    - pattern_type = 'not spiral'    
    '''
    # pattern_type = 'not spiral'  # options: 'spiral', 'not spiral'
    # start_settings = generateCircle(r, section_arc_length, circle_fraction, start_settings, pattern_type)
    # circle_fraction_total = circle_fraction
    # while circle_fraction_total < 1:
    #     start_settings = generateCircle(r, section_arc_length, circle_fraction, start_settings, pattern_type)
    #     circle_fraction_total += circle_fraction


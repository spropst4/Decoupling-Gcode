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
def open_gcode(gcode_txt):
    gcode_list = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            gcode_list.append(myline.strip('\n'))
        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        gcode_list = [x for x in gcode_list if ";--" not in x]  # removes comments
        gcode_list = [x for x in gcode_list if "---" not in x]  # removes comments

        gcode.close()
        return gcode_list
def find_distances(gcode_list):  # s = string to search, ch = character to find
    # ch = character to find
    var_list = ['X', 'Y', 'Z', 'I', 'J', 'G']
    input_line_list = []
    input_var_list = []
    input_G_list = []

    for line in gcode_list:
        gcode_line = line.split(" ")
        result_dist_list = []
        result_var_list = []
        for elem in enumerate(gcode_line):
            for var in var_list:
                if var in elem[1]:
                    result = float(elem[1].strip(var))  # finds location of character, strips it, and outputs numerical number
                    if var == 'G':
                        G_var = int(result)
                    else:
                        result_dist_list.append(result)
                        result_var_list.append(var)

        input_line_list.append(result_dist_list)
        input_var_list.append(result_var_list)
        input_G_list.append(G_var)

    return input_var_list, input_line_list, input_G_list
def segmentCircleG3(input_line, section_arc_length):
    ## find arc_angle
    def find_theta(X, Y, I, J):  # finds angle between intersecting lines
        import math
        from math import atan2
        a = math.atan2(-J, -I)
        b = math.atan2(Y - J, X - I)
        theta = b - a
        return theta

    var_list = input_line[0] # X, Y, I, J
    value_list = input_line[1] # X value, Y value, I value, J value
    G_value = input_line[2]
    X = value_list[0]
    Y = value_list[1]
    I = value_list[2]
    J = value_list[3]

    theta_total = find_theta(X, Y, I, J)
    r = np.sqrt(I**2 + J**2) # r = sqrt(I^2 + J^2)
    if G_value == 3:
        if theta_total <= 0:
            theta_total = 2 * np.pi - abs(theta_total)
        if X > 0:
            sign = -1
        else:
            sign = 1
    else:
        if theta_total < 0:
            theta_total = abs(theta_total)
        else:
            theta_total = 2 * np.pi - theta_total
        if X > 0:
            sign = 1
        else:
            sign = -1

    total_arc_length = r * theta_total

    theta_between_moves = section_arc_length/r
    num_sections = total_arc_length/section_arc_length
    num_sections = round(num_sections)
    theta_between_moves = theta_total/num_sections


    x_prev = r
    y_prev = 0
    theta_for_ij = 0
    theta_for_xy = theta_between_moves

    for c in range(num_sections):

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


        print('\n\rG' +str(G_list) + ' X'+ str(sign*x_rel) + ' Y' + str(sign*y_rel) + ' I' + str(sign*i) + ' J'+ str(sign*j))
        print('pressure_change')
        #print(pressurebox_str_command('serialPort1', pressure))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    gcode_txt_input = 'TestSpiralCirlce_Shell_InputGcode.txt'
    export_file = 'TestConcentricCircle_OutputGcode.txt'
    save_path = 'GradientCircle\\'#'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'



gcode_list = open_gcode(gcode_txt_input)
input_line = find_distances(gcode_list)


print('\nG91')
for i in range(len(input_line[0])):
    var_line = input_line[0][i]
    val_line = input_line[1][i]
    G_list = input_line[2][i]
    if G_list == 3 or G_list == 2:
        input_line_current = [var_line, val_line, G_list]
        segmentCircleG3(input_line_current, 1)
    elif var_line != []:
        code = '\nG1'

        for j in range(len(var_line)):
            code += ' ' + var_line[j] + str(val_line[j])
        print(code)






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
def pressurebox_str_command(com, pressure):
    return str('\n\r' + com + '.write(' + str(setpress(pressure)) + ')')
def pressurebox_toggle_str_command(com):
    return str('\n\r' + com + '.write(' + str(togglepress()) + ')')
def valve_str_command(valve, command):
    return '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', ' +str(command) + ')'
##INPUTS#############################################################################################################
export_file = "231023_PassiveMixingGradient_2mmSwitchOver3Filaments_gcode.txt"
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

# Desired XYZ motion
x_incr = 2 #distance increments to change pressure
x_total = 60 # distance for decr to incr gradient sections (incr or decr) is x_total/2
y_spacing = 3
total_y_dist = 50

z = 0.65 #1  # 0.58
Z_var = "Z"

pressure_start = [40, 70] #[25, 25]
pressure_end = [70, 40]

total_num_pressure_changes = int(x_total / x_incr)

pressure_change_incr1 = 1/3*((pressure_end[0]-pressure_start[0])/(total_num_pressure_changes))
pressure_change_decr2 = 1/3*((pressure_start[1]-pressure_end[1])/(total_num_pressure_changes))

######################################################################################################################

com = ["serialPort2", "serialPort1"]
valve = [7,6]

setpress_list = []
valveON_list = []
valveOFF_list = []
pressure_box_ON_list = []
pressure_box_OFF_list = []
for i in range(len(com)):
    setpress_list.append(pressurebox_str_command(com[i], pressure_start[i]))

    valveON_list.append(valve_str_command(valve[i], True))
    valveOFF_list.append(valve_str_command(valve[i], False))

    pressure_box_ON_list.append(pressurebox_toggle_str_command(com[i]))
    pressure_box_OFF_list.append(pressurebox_toggle_str_command(com[i]))


######
add = 0
import os.path
completeName = os.path.join(save_path, export_file)
pressure1 = pressure_start[0]
pressure2 = pressure_start[1]
with open(completeName, "w") as f:
    for i in range(len(setpress_list)):
        f.write(setpress_list[i])
        f.write(pressure_box_ON_list[i])
        f.write(valveON_list[i])
    f.write('\nG1 X'+str(10))
    for i in range(int(total_y_dist)):
        if (i+1)%2 != 0: # odd fil
            sign = 1
        else:
            sign = -1

        for j in range(total_num_pressure_changes):
            f.write('\nG1 X' + str(sign*x_incr))
            pressure1 += pressure_change_incr1
            pressure2 -= pressure_change_decr2

            if pressure1 <= pressure_end[0]:
                print(pressure1, pressure2)
                print((i+1), (j)*x_incr)
                f.write(pressurebox_str_command(com[0], pressure1))
                f.write(valve_str_command(valve[1], False))
                f.write(pressurebox_str_command(com[1], pressure2))
                f.write(valve_str_command(valve[1], True))

        f.write('\nG1 Y'+str(y_spacing))

    for i in range(len(setpress_list)):
        f.write(pressure_box_OFF_list[i])
        f.write(valveOFF_list[i])



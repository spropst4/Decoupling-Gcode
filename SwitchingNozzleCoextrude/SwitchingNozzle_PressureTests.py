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

##INPUTS#############################################################################################################
export_file = "231130_Gradient_SwitchingNozzle_BLUE_gcode.txt"
save_path = ''#'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

# Desired XYZ motion
x_incr = 2 #distance increments to change pressure
x_total = 80 # distance for decr to incr gradient sections (incr or decr) is x_total/2
repeat = 2
z = 1 #1  # 0.58
Z_var = "Z"


pressure_start = 17.5 #[25, 25]
pressure_end = 27.5
pressure_range = [pressure_start, pressure_end]
avg_pressure = np.average(pressure_range)

total_num_pressure_changes = x_total / x_incr

pressure_change_incr = (pressure_start - pressure_end) / (0.5 * total_num_pressure_changes)
print(pressure_change_incr)
######################################################################################################################

com = "serialPort2"
valve = 7


setpress_start = str('\n\r' + com + '.write(' + str(setpress(pressure_start)) + ')') # material 1
set_avg_pressure = str('\n\r' + com + '.write(' + str(setpress(avg_pressure)) + ')') # material 1
toggleON = str('\n\r'+com +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

valveON = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', True)'
valveOFF = '\n{aux_command}WAGO_ValveCommands(' + str(valve) + ', False)'


######
add = 0
import os.path
completeName = os.path.join(save_path, export_file)
current_pressure = pressure_start
prev_pressure = pressure_start
with open(completeName, "w") as f:
    f.write(setpress_start)
    #f.write(set_avg_pressure)
    f.write(toggleON)
    f.write(valveON)
    f.write('\nG1 X'+str(10))

    # if pressure_start < avg_pressure:
    #     f.write(valveOFF)
    # f.write(setpress_start)
    # if pressure_start < avg_pressure:
    #     f.write(valveON)
    f.write('\nG1 X'+str(x_incr))


    for j in range(repeat):
        for i in range(int(total_num_pressure_changes/2)):

            current_pressure -= pressure_change_incr
            if current_pressure < prev_pressure:
                f.write(valveOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(current_pressure)) + ')'))
            if current_pressure < prev_pressure:
                f.write(valveON)
            f.write('\nG1 X' + str(x_incr))
            prev_pressure = current_pressure
            print(current_pressure)

        for i in range(int(total_num_pressure_changes/2)):
            current_pressure += pressure_change_incr
            if current_pressure < prev_pressure:
                f.write(valveOFF)
            f.write(str('\n\r' + com + '.write(' + str(setpress(current_pressure)) + ')'))
            if current_pressure < prev_pressure:
                f.write(valveON)
            f.write('\nG1 X' + str(x_incr))
            prev_pressure = current_pressure
            print(current_pressure)

    f.write(valveOFF)
    f.write(toggleOFF)






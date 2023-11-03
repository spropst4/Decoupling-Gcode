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
export_file = "231103_DiscreteSwitchingMixingGradient_gcode.txt"
save_path = 'C:\\Users\\MuellerLab_HPC\\PycharmProjects\\Gcode_generator\\SPropst_Decoupling'

# Desired XYZ motion
x_total = 28 # distance for decr to incr gradient sections (incr or decr) is x_total/2
y_spacing = 1
total_y_dist = 28
z = 0.65 #1  # 0.58
Z_var = "Z"

ratio = [[28,5], [27,23], [26,24], [25.5, 25.5], [24, 26], [23,27], [5, 28]]#[[20,24],[22, 22], [23.5, 21],[24, 20] ,[25.5,18],[26,17],[26.5,16], [26.5, 10]]
adjust_pressure = -3.5
num_fil = int(total_y_dist/y_spacing)
switch = round(num_fil/ len(ratio))
new_num_fil = switch*len(ratio)
print(new_num_fil)
######################################################################################################################

com = ["serialPort1", "serialPort2"]
valve = [6,7]

setpress_list = []
valveON_list = []
valveOFF_list = []
pressure_box_ON_list = []
pressure_box_OFF_list = []
for i in range(len(com)):
    setpress_list.append(pressurebox_str_command(com[i], ratio[0][i]+ adjust_pressure))

    valveON_list.append(valve_str_command(valve[i], True))
    valveOFF_list.append(valve_str_command(valve[i], False))

    pressure_box_ON_list.append(pressurebox_toggle_str_command(com[i]))
    pressure_box_OFF_list.append(pressurebox_toggle_str_command(com[i]))


######
add = 0
import os.path
completeName = os.path.join(save_path, export_file)
pressure1 = ratio[0][0] + adjust_pressure
pressure2 = ratio[0][1] + adjust_pressure
with open(completeName, "w") as f:
    for i in range(len(com)):
        f.write(setpress_list[i])
        f.write(pressure_box_ON_list[i])
        f.write(valveON_list[i])

    f.write('\nG1 X'+str(10))
    for i in range(new_num_fil):
        if (i+1)%2 != 0: # odd fil
            sign = 1
        else:
            sign = -1
        print('fil_number = ', i + 1)
        f.write('\nG1 X' + str(sign * x_total))
        f.write('\nG1 Y' + str(y_spacing))
        if (i+1)%switch == 0 and (i+1) != new_num_fil:
            index = int(i/switch) +1
            print('index = ', index)
            pressure1 = ratio[index][0] + adjust_pressure
            pressure2 = ratio[index][1] + adjust_pressure

            if pressure1<prev_press1:
                f.write(valve_str_command(valve[0], False))
            if pressure2 < prev_press2:
                f.write(valve_str_command(valve[1], False))
            f.write(pressurebox_str_command(com[0], pressure1))
            f.write(pressurebox_str_command(com[1], pressure2))
            if pressure1<prev_press1:
                f.write(valve_str_command(valve[0], True))
            if pressure2 < prev_press2:
                f.write(valve_str_command(valve[1], True))

        prev_press1 = pressure1
        prev_press2 = pressure2
        print(pressure1,  pressure2)

    for i in range(len(setpress_list)):
        f.write(pressure_box_OFF_list[i])
        f.write(valveOFF_list[i])



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
    finalcommand = ('\\x05\\x02') + format_command + format_checksum + str('\\x03')
    finalcommand = finalcommand.strip('\r').strip('\n')
    finalcommand = '"' + finalcommand + '"'
    return finalcommand
def togglepress():
    # IMPORTS
    import serial
    from codecs import encode
    from textwrap import wrap
    toggle = str('"\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03"')
    return toggle

export_gcode_txt = "Aerotech_SemiCircle_CoreShell_gcode.txt"
circle_diam = 30
filament_width = 1
z = 1
Z_var = "D"
Z_start = -150 + z

# Feedrate
feed = 15  # mm/sec
ramprate = 1000 # mm/s/s

pressure = [22, 28] # 1 is core, 2 is shell
com = [4, 5] #core 1, shell 2

## Are you applying offsets?
apply_offset = True
offset = 3                                    # 1.4  # for F=15 #2.5mm for F=25

## Apply intro?
intro_flag = True                               # mark True if you want to add an intro; mark False if you don't want to add an intro
ending_flag = True                              # mark True if you want to add an ending; mark False if you don't want to add an ending
intro_gcode = "Spropst_aerotech_intro.txt"
ending_gcode = "Spropst_aerotech_end.txt"

######################################################################################################################
file_name = ["$hFile1", "$hFile2"]

### Define commands

setpress1 = str('\n\rFILEWRITE ' + str(file_name[0]) + ", "+ str(setpress(pressure[0])) + " 'Core: P = " + str(pressure[0])+ " psi") #set pressure material 1 - CORE
setpress2 = str('\n\rFILEWRITE ' + str(file_name[1]) + ", "+ str(setpress(pressure[1])) + " 'Shell P = " + str(pressure[1])+ " psi") #set pressure material 1 - CORE

toggleON_1 = str('\n\rFILEWRITE ' + str(file_name[0]) + ", "+ str(togglepress())+ " 'Core ON")# turn on material Core
toggleOFF_1 = str('\n\rFILEWRITE ' + str(file_name[0]) + ", "+ str(togglepress())+ " 'Core OFF")

toggleON_2 = str('\n\rFILEWRITE ' + str(file_name[1]) + ", "+ str(togglepress())+ " 'Shell ON")  # turn on shell
toggleOFF_2 = str('\n\rFILEWRITE ' + str(file_name[1]) + ", "+ str(togglepress())+ " 'Shell OFF")

if apply_offset == False:
    offset = 0

import numpy as np
Gcommand_list = []
X_list = []
Y_list = []
I_list = []
J_list = []
Command_list = []
i = 0

while circle_diam > 0:
    if apply_offset == False:
        if (i + 1) % 2 != 0:  ## odd lines
            if i > 0:
                circle_diam -= 2 * filament_width
            Gcommand_list.append("G3")
            X_list.append(-circle_diam)
            I_list.append(-circle_diam / 2)
            Y_list.append(0)
            J_list.append(0)
            Command_list.append(True)

        else:
            Gcommand_list.append("G3")
            X_list.append(circle_diam)
            I_list.append(circle_diam / 2)
            Y_list.append(0)
            J_list.append(0)
            Command_list.append(True)

            Gcommand_list.append("G1")
            X_list.append(-filament_width)
            I_list.append(0)
            Y_list.append(0)
            J_list.append(0)
            Command_list.append(False)


    else:
        if (i+1)%2 != 0: # odd
            if i > 0:
                circle_diam -= 2 * filament_width
            R = circle_diam / 2
            if R > 0:
                theta = offset / R  # calculate central angle for offset
            Gcommand_list.append("G3")
            X_offset = - (R  * np.cos(theta) + R)
            Y_offset = R * np.sin(theta)
            I_offset = -circle_diam/2
            J_offset = 0

            X_list.append(X_offset)
            Y_list.append(Y_offset)
            I_list.append(I_offset)
            J_list.append(J_offset)
            Command_list.append(True)

        else:
            Gcommand_list.append("G3")
            X_offset = (R - filament_width) * np.cos(theta)) * 2
            Y_offset = -(R * np.sin(theta)) * 2
            I_offset = R * np.cos(theta)
            J_offset = -R * np.sin(theta)

            X_list.append(X_offset)
            Y_list.append(Y_offset)
            I_list.append(I_offset)
            J_list.append(J_offset)
            Command_list.append(True)


            Gcommand_list.append("G3")
            X_remain = R - R*np.cos(theta)
            Y_remain = R*np.sin(theta)
            I_remain = -R*np.cos(theta)
            J_remain = R*np.sin(theta)

            X_list.append(X_remain)
            Y_list.append(Y_remain)
            I_list.append(I_remain)
            J_list.append(J_remain)
            Command_list.append(False)

            Gcommand_list.append("G1")
            X_list.append(-filament_width)
            Y_list.append(0)
            I_list.append(0)
            J_list.append(0)
            Command_list.append(False)

    i += 1

print(Gcommand_list)
print(X_list)
print(Y_list)
print(I_list)
print(J_list)
print(Command_list)

## Writes aerotech intro to final file (only runs if you flagged it as true)
def intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start):
    with open(intro_gcode, "r") as g:
        with open(export_gcode_txt, 'w') as f:
            for line in g:
                line = line.replace('{file_name1}', file_name[0]).replace('{file_name2}', file_name[1]).replace('{Z_var}', Z_var).replace('{ramprate}', str(ramprate)).replace('{feed}', str(feed)).replace('{Z_start}', str(Z_start))
                line = line.replace('{com1}', str(com[0])).replace('{com2}', str(com[1]))
                f.write(line)
        g.close()

    return f
    f.close()

if intro_flag == True:
    intro_export = intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start)
    type_open = "a"
else:
    type_open = "w"

'''Outputs "traditional" gcode '''
with open(export_gcode_txt, type_open) as f:
    f.write(setpress1)
    f.write(setpress2)
    f.write(toggleON_1)
    f.write(toggleON_2)
    # f.write('\n\rG1 X-10')
    M1_ON = True
    for i in range(len(Gcommand_list)):
        if Gcommand_list[i] == "G3":
            Gcommand_list[i] = "CCW"
            if I_list[i] == 0 and J_list[i] == 0:
                f.write("\n\r")
            else:
                f.write("\n\r" + Gcommand_list[i] + " X" + str(X_list[i]) + " Y" + str(Y_list[i]) + " I" + str(I_list[i]) + " J" + str(J_list[i]))
        else:
            f.write("\n\r" + Gcommand_list[i] + " X" + str(X_list[i]))
        if Command_list[i] == True:
            if M1_ON == True:
                f.write(toggleOFF_1)
                M1_ON = False
            else:
                f.write(toggleON_1)
                M1_ON = True
            if i == len(Gcommand_list) and M1_ON == True:
                f.write(toggleOFF_1)
    f.write(toggleOFF_2)

## Writes aerotech ending to final file (only runs if you flagged it as true)
def ending(ending_gcode, export_gcode_txt, Z_var):
    with open(ending_gcode, "r") as g:
        with open(export_gcode_txt, 'a') as f:
            f.write('\n\r')
            for line in g:
                f.write(line.replace('{Z_var}', Z_var).replace('{file_name1}', file_name[0]).replace('{file_name2}', file_name[1]))
        g.close()

    return f
    f.close()
if ending_flag == True:
    ending_export = ending(ending_gcode, export_gcode_txt, Z_var)

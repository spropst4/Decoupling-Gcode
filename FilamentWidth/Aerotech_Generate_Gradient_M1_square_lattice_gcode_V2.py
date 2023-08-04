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

##INPUTS#############################################################################################################
export_file = "Aerotech_Generate_Gradient_M1_square_lattice_gcode_V2.txt"
# Desired XYZ motion
incr = 1
total = 30
fil_spacing = 3
total_lines = 12

z_start = 0.6 #1  # 0.58
z_layers = 0.45
z_end_relative = .8 # how much z goes up by
Z_var = "D"
z_incr = z_end_relative / (total / incr) # when travelling in x-direction
print(z_incr)

pressure_start_original = 26 #[25, 25]
pressure_end_original = 46
num_layers = 2

######################################################################################################################
file_name = ["$hFile1", "$hFile2"]
com = [6,5] #core 1, shell 2

#setpress1 = str('\n\rFILEWRITE ' + str(file_name[0]) + ", "+ str(setpress(pressure_start)))

toggleON = str('\n\rFILEWRITE ' + str(file_name[0]) + ", "+ str(togglepress()))# + '\n\rDWELL 0.5')
toggleOFF = toggleON

## Defined XYZ (don't change
add = 0
pressure_add = 0
z_factor = 1
with open(export_file, "w") as f:
    for layers in range(num_layers):
        z_incr_height = 0
        pressure_start = pressure_start_original
        pressure_end = pressure_end_original
        pressure_add = 0

        if layers != 0:
            z_factor += 0.05
            print(z_factor)

        if (layers +1)%2 != 0: # odd layers
            f.write("\n\rG0 " + Z_var + str(1))
            f.write('\n\rG90')
            f.write('\n\rG0 X150 Y50 ' +Z_var +str(-(150 - z_start) + (layers)*z_layers))
            f.write('\n\rG91')
            for j in range(total_lines):
                for i in range(int(total / incr) + 1):
                    if i == 0:
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write(toggleON)
                        f.write('\n\rDWELL 0.15')
                        f.write('\n\rG1 Y' + str(incr + 6))# + " " + Z_var + str(z_incr * z_factor))

                    elif i + 1 == (int(total / incr) +1):
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write('\n\rG1 Y' + str(incr + 6))# + " " + Z_var + str(z_incr * z_factor))

                    else:
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write("\nG1 Y" + str(incr) + " " + Z_var + str(z_incr * z_factor))


                    pressure_add += (pressure_end - pressure_start)/ (total / incr)

                pressure_start += 2
                pressure_end += 2
                z_incr_height = z_incr*2

                f.write(toggleOFF)
                f.write("\n\rG1 X" + str(fil_spacing))
                f.write("\n\rG1 Y" + str(-total - 12 - incr)) #+ " " + Z_var + str(-z_factor * (z_end_relative - z_incr_height)))

                if (j+1) != total_lines:
                    f.write("\n\rG0 " + Z_var + str(-(z_end_relative)))
                    f.write("\n\rG0 " + Z_var + str((z_incr_height)))
                pressure_add = 0

        if (layers + 1)%2 == 0: #even layers
            f.write("\n\rG0 " + Z_var + str(1))

            f.write('\n\rG90')
            f.write('\n\rG0 X147 Y53 '+Z_var + str(-(150 - z_start) + (layers)*z_layers))
            f.write('\n\rG91')

            z_incr_height = 0
            pressure_start = pressure_start_original
            pressure_end = pressure_end_original
            pressure_add = 0
            for j in range(total_lines):
                for i in range(int(total / incr) + 1):
                    if i == 0:
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write(toggleON)
                        f.write('\n\rDWELL 0.15')
                        f.write('\n\rG1 X' + str(incr + 6) )#+ " " + Z_var + str(z_incr * z_factor))

                    elif i + 1 == (int(total / incr) + 1):
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write('\n\rG1 X' + str(incr + 6))# + " " + Z_var + str(z_incr * z_factor))

                    else:
                        f.write(str('\n\rFILEWRITE ' + str(file_name[0]) + ", " + str(setpress(pressure_start + pressure_add)) + ' ; P = ' + str(pressure_start + pressure_add)))
                        f.write("\nG1 X" + str(incr) + " " + Z_var + str(z_incr * z_factor))


                    pressure_add += (pressure_end - pressure_start)/ (total / incr)

                pressure_start += 1
                pressure_end += 2
                z_incr_height = z_incr*2
                f.write(toggleOFF)

                f.write("\n\rG1 Y" + str(fil_spacing))
                f.write("\n\rG1 X" + str(-total - 12 - incr))
                if (j + 1) != total_lines:
                    f.write("\n\rG0 " + Z_var + str(-(z_end_relative)))
                    f.write("\n\rG0 " + Z_var + str((z_incr_height)))


                pressure_add = 0




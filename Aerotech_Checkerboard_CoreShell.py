def setpress(pressure):
    # IMPORTS
    from codecs import encode
    from textwrap import wrap

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
export_gcode_txt = "Aerotech_Checkerboard_CoreShell_gcode.txt"    # export gcode as txt file (i.e., must include .txt)

intro_flag = True       # False             # mark True if you want to add an intro; mark False if you don't want to add an intro
ending_flag = True      # False             # mark True if you want to add an ending; mark False if you don't want to add an ending
intro_gcode = "Spropst_aerotech_intro.txt"
ending_gcode = "Spropst_aerotech_end.txt"
#############################################

# Desired XYZ motion
x = 10
y = 1 #1
z = 1 #1  # 0.58
Z_var = "Z"

col = 3
rows = 3

# Feedrate
F = 25 # mm/sec
F = F * 60  # mm/min

pressure = [20, 27] # 1 is core, 2 is shell

#########################################################################

com = ["FILEWRITE $hFile1,", "FILEWRITE $hFile2,"]

setpressCore =str('\n\r' + com[0] + str(setpress(pressure[0]))) #set pressure material 1 - CORE
setpressSHELL =str('\n\r' + com[1] + str(setpress(pressure[1]))) #set pressure material 2 - SHELL


toggleON_CORE = str('\n\r' + com[0] + str(togglepress())) # start 1st material
toggleOFF_CORE = toggleON_CORE

toggleON_SHELL_start = str('\n\r' + com[1] + str(togglepress()))  #start 2nd material
toggleOFF_SHELL_end = toggleON_SHELL_start


toggleON_SHELL = str('\n\r') #str('\n\r' + com[1] + '.write(' + str(togglepress()) + ')')  #start 2nd material
toggleOFF_SHELL = toggleON_SHELL

if apply_offset == yes:
    offset = offset
    pause = pause

    offset_pos = "\n\rG1 X" + str(offset) + "\n\r"
    offset_neg = "\n\rG1 X" + str(-offset) + "\n\r"

    offset_pos2 = ""  # "\n\rG1 X" + str(offset) + "\n\r" #material 2
    offset_neg2 = ""  # "\n\rG1 X" + str(-offset) + "\n\r" #material 2

else:
    offset = 0
    pause = 0
    offset_pos = ""
    offset_neg = ""

    offset_pos2 = ""  # material 2
    offset_neg2 = ""  # material 2

## Defined XYZ (don't change
X = " X" + str(x - offset)
Y = " Y" + str(y)
Z = " " + Z_var + str(z)

_X = " X" + str(-x + offset)
_Y = " Y" + str(-y)
_Z = " " + Z_var + str(-z)

move_pos_x = "\nG1" + X
move_neg_x = "\nG1" + _X
move_y = "\n\rG1" + Y + "\n\r"

lines = int(x / y)
print(lines)
## material 2 move x
move_pos_2 = move_pos_x  # "\nG0" + X
move_neg_2 = move_neg_x  # "\nG0" + _X

### combining varaibles from old codes...
material_1_ON = toggleON_CORE
material_1_OFF = toggleOFF_CORE

material_2_ON = toggleON_SHELL
material_2_OFF = toggleOFF_SHELL


## Writes aerotech intro to final file (only runs if you flagged it as true)
def intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start):
    with open(intro_gcode, "r") as g:
        with open(export_gcode_txt, 'w') as f:
            for line in g:
                line = line.replace('{file_name}', file_name[0]).replace('{Z_var}', Z_var).replace('{ramprate}', str(ramprate)).replace('{feed}', str(feed)).replace('{Z_start}', str(Z_start))
                line = line.replace('{com}', str(com[0]))
                line = line.replace('{setpress}', str(setpress_val))
                f.write(line)
        g.close()

    return f
    f.close()
if intro_flag == True:
    intro_export = intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start)
    type_open = "a"
else:
    type_open = "w"

with open(export_gcode_txt, type_open) as f:
    f.write("\n\r;------------Set Pressures------------")
    f.write(setpressCore)
    f.write(setpressSHELL)
    # f.write("time.sleep(2850/1000);")
    f.write(toggleON_SHELL_start)
    # f.write("\n\rG1 X5")
    if col % 2 == 0:  # even number of rows and col
        for r in range(rows):
            f.write("\n\r;-------------ROW " + str(r + 1) + "-------------")
            if (r + 1) % 2 > 0:  # odd row
                for l in range(lines):
                    f.write("\n\r;---------LINE " + str(l + 1) + "---------")
                    if (l + 1) % 2 > 0:  # odd line
                        for c in range(col):
                            if (c + 1) == col:
                                f.write(material_2_ON)
                                f.write("\r\nG1 X" + str(x))
                                f.write(move_y)


                            elif (c + 1) % 2 > 0:  # odd column
                                if (c + l + r) == 0:  # first line, row, column
                                    f.write(material_1_ON)
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)

                                elif (c + l) == 0:  # first line, row, column
                                    f.write(material_1_ON)
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)

                                else:
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)

                            else:  # even column
                                f.write(material_2_ON)
                                f.write(move_pos_2)
                                f.write(material_2_OFF)
                                f.write(offset_pos)


                    else:  # even line
                        for c in range(col):
                            if (c + 1) == col:
                                if (l + 1) == lines:
                                    f.write(material_1_ON)
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)
                                    f.write(move_y)

                                else:
                                    f.write(material_1_ON)
                                    f.write("\r\nG1 X" + str(-x))
                                    f.write(move_y)


                            elif (c + 1) % 2 == 0:  # even column
                                f.write(material_1_ON)
                                f.write(move_neg_x)
                                f.write(material_1_OFF)
                                f.write(offset_neg)


                            else:  # odd column
                                if (c == 0):
                                    f.write(move_neg_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_neg)


                                else:
                                    #                                    f.write(material_2_ON)
                                    f.write(move_neg_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_neg)


            else:  # even rows
                for l in range(lines):
                    f.write("\n\r;---------LINE " + str(l + 1) + "---------")
                    if (l + 1) % 2 > 0:  # odd line
                        for c in range(col):
                            if (c + 1) == col:
                                f.write(material_1_ON)
                                f.write("\r\nG1 X" + str(x))
                                f.write(move_y)

                            elif (c + 1) % 2 > 0:  # odd column
                                if (c + l) == 0:  # first line and column
                                    f.write(material_2_ON)
                                    f.write(move_pos_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_pos)

                                else:
                                    f.write(move_pos_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_pos)


                            else:  # even column
                                f.write(material_1_ON)
                                f.write(move_pos_x)
                                f.write(material_1_OFF)
                                f.write(offset_pos)


                    else:  # even line
                        for c in range(col):
                            if (c + 1) == col:
                                if (l + 1) == lines:
                                    f.write(material_2_ON)
                                    f.write(move_neg_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_neg)
                                    f.write(move_y)

                                else:
                                    f.write(material_2_ON)
                                    f.write("\r\nG1 X" + str(-x))
                                    f.write(move_y)



                            elif (c + 1) % 2 == 0:  # even column
                                f.write(material_2_ON)
                                f.write(move_neg_2)
                                f.write(material_2_OFF)
                                f.write(offset_neg)


                            else:  # odd column
                                if (c == 0):
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)

                                else:
                                    f.write(material_1_ON)
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)


    ## odd number of rows and col
    else:
        for r in range(rows):
            f.write("\n\r;-------------ROW " + str(r + 1) + "-------------")
            if (r + 1) % 2 > 0:  # odd row
                for l in range(lines):
                    f.write("\n\r;---------LINE " + str(l + 1) + "---------")
                    if (l + 1) % 2 > 0:  # odd line
                        for c in range(col):
                            if (c + 1) == col:
                                f.write(material_1_ON)
                                f.write(offset_pos)
                                f.write("\r\nG1 X" + str(x))
                                f.write(move_y)

                            elif (c + 1) % 2 > 0:  # odd column
                                if (c + l + r) == 0:  # first line, row, column
                                    f.write(material_1_ON)
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)

                                elif (c + l) == 0:  # first line, column
                                    f.write(material_1_ON)
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)

                                else:
                                    f.write(move_pos_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_pos)


                            else:  # even column
                                f.write(material_2_ON)
                                f.write(move_pos_2)
                                f.write(material_2_OFF)
                                f.write(offset_pos2)

                    else:  # even line
                        for c in range(col):
                            if (c + 1) == col:
                                if (l + 1) == lines:
                                    f.write(material_1_ON)
                                    f.write(offset_neg)
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)
                                    f.write(move_y)

                                else:
                                    f.write(material_1_ON)
                                    f.write(offset_neg)
                                    f.write("\r\nG1 X" + str(-x))
                                    f.write(move_y)



                            elif (c + 1) % 2 == 0:  # even column
                                f.write(material_2_ON)
                                f.write(move_neg_2)
                                f.write(material_2_OFF)
                                f.write(offset_neg2)


                            else:  # odd column
                                if (c == 0):
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)

                                else:
                                    f.write(material_1_ON)
                                    f.write(offset_neg)
                                    f.write(move_neg_x)
                                    f.write(material_1_OFF)
                                    f.write(offset_neg)

            else:  # even rows
                for l in range(lines):
                    f.write("\n\r;---------LINE " + str(l + 1) + "---------")
                    if (l + 1) % 2 > 0:  # odd line
                        for c in range(col):
                            if (c + 1) == col:
                                f.write(material_2_ON)
                                f.write("\r\nG1 X" + str(x))
                                f.write(move_y)

                            elif (c + 1) % 2 > 0:  # odd column
                                if (c + l) == 0:  # first line, column
                                    f.write(material_2_ON)
                                    f.write(move_pos_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_pos2)

                                else:
                                    f.write(move_pos_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_pos2)


                            else:  # even column
                                f.write(material_1_ON)
                                f.write(offset_pos)
                                f.write(move_pos_x)
                                f.write(material_1_OFF)
                                f.write(offset_pos)

                    else:  # even line
                        for c in range(col):
                            if (c + 1) == col:
                                if (l + 1) == lines:
                                    f.write(material_2_ON)
                                    # f.write(move_neg_2)
                                    f.write("\r\nG1 X" + str(-x))
                                    f.write(material_2_OFF)
                                    f.write(offset_neg2)
                                    f.write(move_y)

                                else:
                                    f.write(material_2_ON)
                                    # f.write(move_neg_2)
                                    f.write("\r\nG1 X" + str(-x))
                                    f.write(move_y)


                            elif (c + 1) % 2 == 0:  # even column
                                f.write(material_1_ON)
                                f.write(offset_neg)
                                f.write(move_neg_x)
                                f.write(material_1_OFF)
                                f.write(offset_neg)

                            else:  # odd column
                                if (c == 0):
                                    f.write(move_neg_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_neg2)

                                else:
                                    f.write(material_2_ON)
                                    f.write(move_neg_2)
                                    f.write(material_2_OFF)
                                    f.write(offset_neg2)

    f.write(toggleOFF_SHELL_end)

## Writes aerotech ending to final file (only runs if you flagged it as true)
def ending(ending_gcode, export_gcode_txt, Z_var):
    with open(ending_gcode, "r") as g:
        with open(export_gcode_txt, 'a') as f:
            f.write('\n\r')
            for line in g:
                f.write(line.replace('{Z_var}', Z_var))
        g.close()

    return f
    f.close()
if ending_flag == True:
    ending_export = ending(ending_gcode, export_gcode_txt, Z_var)
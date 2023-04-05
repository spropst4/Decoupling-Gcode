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
    format_command = '\\x' + format_command
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
    toggle = str("b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03'")
    return toggle


## this version turns on only material 1

### Are you checking pattern on Qndirty/do you want G0 movements?
G0_moves = False  # false meanse all moves will be G1

### Do you want the material to stay on during y-movves?
y_move_ON = True  # false means you want material to turn off during y-moves

## Are you applying offsets and initial pause?
apply_offset = False
offset = 2.5  # 1.4  # for F=15 #2.5mm for F=25

##INPUTS#############################################################################################################
# Desired XYZ motion
x = 10
y = 0.58  # 1
z = 0.6  # 1  # 0.58
Z_var = "Z"

col = 3
rows = 3

total_width = col * x
total_height = rows * x
number_lines_to_print = int(total_height / y)
print("number_lines_to_print = ", number_lines_to_print)

lines_per_row = int(number_lines_to_print / rows)
print("lines_per_row (rounded to a whole number) = ", lines_per_row)
number_lines_to_print = lines_per_row * rows
print("number_lines_to_print (updated so that number of lines per row is a whole number) = ", number_lines_to_print)

# Feedrate
F = 10  # mm/sec
F = F * 60  # mm/min

pressure = [35, 35] # 1 is core, 2 is shell

######################################################################################################################
com = ["serialPort1", "serialPort2"] # 1 is core, 2 is shell

setpressCore = str('\n\r' + com[0] + '.write(' + str(setpress(pressure[0])) + ')') #  core
setpressShell = str('\n\r' + com[1] + '.write(' + str(setpress(pressure[1])) + ')') # shell 1
#setpressCore = '\n\r Pressure Material 1'
# setpressShell = '\n\r Pressure Material 2'

toggleON_Core = str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')') # turn on material Core
toggleOFF_Core = toggleON_Core
# toggleON_Core = '\n\rMaterial 1 ON'
# toggleOFF_Core = '\n\rMaterial 1 OFF'

toggleON_Shell = str('\n\r' + com[1] + '.write(' + str(togglepress()) + ')')  # turn on shell
toggleOFF_Shell = toggleON_Shell #'\n'  # "\nM792 ;SEND Ultimus_IO["+str(comRight)+"]= 0" #stop 2nd material
# toggleON_Shell = '\n\rMaterial 2 ON'
# toggleOFF_Shell = '\n\rMaterial 2 OFF'

if apply_offset == False:
    offset = 0

## Defined XYZ (don't change
X = " X" + str(x - offset)
Y = " Y" + str(y)
Z = " " + Z_var + str(z)

_X = " X" + str(-x + offset)
_Y = " Y" + str(-y)
_Z = " " + Z_var + str(-z)

move_pos_x = "\nG1" + X
move_neg_x = "\nG1" + _X
move_pos_y = "\n\rG1" + Y
move_neg_y = "\n\rG1" + _Y

move_pos_x_offset = "\nG1 X" + str(offset)
move_neg_x_offset = "\nG1 X" + str(-offset)

row_count = 1
material_ON = 1
with open("1DGC_Generate_Checkerboard_CoreShell_gcode.txt", 'w') as f:
    f.write("\n\r;------------Set Pressures------------")
    f.write(setpressCore)
    f.write(setpressShell)
    f.write("\n\r;------------Toggle on Shell and Core------------")
    f.write(toggleON_Shell)
    f.write(toggleON_Core)
    f.write("\nG1 X5")
    for i in range(number_lines_to_print):
        current_line = i + 1
        if i > 1:
            f.write("\n------------- new line -------------------")

        ############ defining the x-movements; i.e., is it moving + or -, are there G0 moves, are there offset
        if current_line % 2 != 0:  ## odd line
            move_x_1 = move_pos_x
            move_x_code_offset_1 = move_pos_x_offset
            move_x_final_col_1 = "\nG1 X" + str(x)
            move_x_2 = move_x_1
            move_x_code_offset_2 = move_x_code_offset_1
            move_x_final_col_2 = move_x_final_col_1

            if G0_moves == True:
                move_x_2 = "\nG0" + X
                move_x_code_offset_2 = "\nG0 X" + str(offset)
                move_x_final_col_2 = "\nG0 X" + str(x)
        else:
            move_x_1 = move_neg_x
            move_x_code_offset_1 = move_neg_x_offset
            move_x_final_col_1 = "\nG1 X" + str(-x)
            move_x_2 = move_x_1
            move_x_code_offset_2 = move_x_code_offset_1
            move_x_final_col_2 = move_x_final_col_1

            if G0_moves == True:
                move_x_2 = "\nG0" + _X
                move_x_code_offset_2 = "\nG0 X" + str(-offset)
                move_x_final_col_2 = "\nG0 X" + str(-x)

        ############ deterning what material to turn on or off
        if current_line <= number_lines_to_print / rows * row_count:
            for j in range(col):
                if (j + 1) == col:  ## if the last column
                    if material_ON == 1:
                        move_x_code = move_x_final_col_1
                        move_x_code_offset = '\r'
                        switchOFF = toggleOFF_Core
                        switchON = toggleON_Core
                    elif material_ON == 2:
                        move_x_code = move_x_final_col_2
                        move_x_code_offset = '\r'
                        switchOFF = '\r'
                        switchON = '\r'

                    switch = switchOFF + move_pos_y + switchON  ### to turn material off during y-moves
                    if y_move_ON == True:
                        switch = '\n' + move_pos_y  ### to keep material on during y-moves

                    if current_line == number_lines_to_print:  ## if the last column and the end of the print
                        if material_ON == 1:
                            switch = toggleOFF_Core
                        elif material_ON == 2:
                            switch = toggleOFF_Shell
                elif material_ON == 1:
                    move_x_code = move_x_1
                    move_x_code_offset = move_x_code_offset_1
                    switch = toggleOFF_Core
                    material_ON = 2
                elif material_ON == 2:
                    move_x_code = move_x_2
                    move_x_code_offset = move_x_code_offset_2
                    switch = toggleON_Core
                    material_ON = 1

                ############ actually writing the code to the text file... finally
                f.write(move_x_code)
                f.write('\n;--------------')
                f.write(switch)
                if apply_offset == True:
                    f.write(move_x_code_offset)

            ############ determines what to do on the last lines of each row
            if current_line == number_lines_to_print / rows * row_count and current_line != number_lines_to_print:  ## if the last line of the row and not the last line in the print
                f.write("\r\n;--------------------------------- new row --------------------------------")
                if material_ON == 1:  # switching from odd rows to even row
                    switch = toggleON_2 + toggleOFF_1
                    material_ON = 2
                else:
                    switch = toggleON_1 + toggleOFF_2
                    material_ON = 1
                f.write(switch)
                row_count += 1  ## moves loop to next row block

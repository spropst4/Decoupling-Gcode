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

def write_setpress_Automation1(com, pressure, dwell): # com as list, pressure as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecSetPressure(' + str(com) + ', ' + str(pressure) + ')")' #+ '\nDwell(' +str(dwell) + ')'

def write_togglepress_Automation1(com, dwell): # com as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecTogglePressure(' + str(com) + ')")' #+ '\nDwell(' +str(dwell) + ')'

### Are you checking pattern on Qndirty/do you want G0 movements?
G0_moves = False  # false meanse all moves will be G1

### Do you want the material to stay on during y-movves?
y_move_ON = True  # false means you want material to turn off during y-moves

## Are you applying offsets and initial pause?
apply_offset = True
offset = 4 # 1.4  # for F=15 #2.5mm for F=25

## Exporting Information ########################################################################################################
export_gcode_txt = "231110_Automation1_Checkerboard_SwitchingNozzle_gcode.txt"    # export gcode as txt file (i.e., must include .txt)

intro_flag = True       # False             # mark True if you want to add an intro; mark False if you don't want to add an intro
ending_flag = False      # False             # mark True if you want to add an ending; mark False if you don't want to add an ending
intro_gcode = "SPropst_automation1_intro.txt"
ending_gcode = "Spropst_aerotech_end.txt"

type_test = "not accel"

############# INPUTS ################################
# Desired XYZ motion
x = 10
y = 1 # 1
z = 1  # 1  # 0.58
Z_var = "C"
Z_start = -150 + z

col = 3
rows = 1

pressure = [35, 35]

# Feedrate
feed = 15  # mm/sec
ramprate = 1000 # mm/s/s

com = [9, 10]

## Calculating width, height, number of lines to print, etc. ###
total_width = col * x
total_height = rows * x
number_lines_to_print = round(total_height / y)

if type_test == "accel":
    number_lines_to_print = number_lines_to_print*3

print("number_lines_to_print = ", number_lines_to_print)

lines_per_row = round(number_lines_to_print / rows)
print("lines_per_row (rounded to a whole number) = ", lines_per_row)
number_lines_to_print = lines_per_row * rows
print("number_lines_to_print (updated so that number of lines per row is a whole number) = ", number_lines_to_print)

######################################################################################################################

setpress1 = write_setpress_Automation1([com[0]], [pressure[0]], 0.15)
setpress2 = write_setpress_Automation1([com[1]], [pressure[1]], 0.15)

toggleON_1 = write_togglepress_Automation1([com[0]], 0.15)
toggleOFF_1 = write_togglepress_Automation1([com[0]], 0.15)

toggleON_2 = write_togglepress_Automation1([com[1]], 0.15)
toggleOFF_2 = write_togglepress_Automation1([com[1]], 0.15)


if apply_offset == False:
    offset = 0

## Defined XYZ (don't change
# X = " X" + str(x - offset)
# Y = " Y" + str(y)
# Z = " " + Z_var + str(z)
#
# _X = " X" + str(-x + offset)
# _Y = " Y" + str(-y)
# _Z = " " + Z_var + str(-z)


X = " X" + str(x)
Y = " Y" + str(y)
Z = " " + Z_var + str(z)

_X = " X" + str(-x)
_Y = " Y" + str(-y)
_Z = " " + Z_var + str(-z)

move_pos_x = "\nG1" + X
move_neg_x = "\nG1" + _X
move_pos_y = "\n\rG1" + Y
move_neg_y = "\n\rG1" + _Y

move_pos_x_offset = "\nG1 X" + str(x-offset)
move_neg_x_offset = "\nG1 X" + str(-x + offset)

move_pos_x_end_line = "\nG1 X" + str(x+offset)
move_neg_x_end_line = "\nG1 X" + str(-x - offset)

move_pos_y_offset =  "\nG1 Y" + str(y-offset)
move_pos_y_remain = '\nG1 Y' + str(offset)
if apply_offset == False:
    move_pos_y_remain = ''



row_count = 1
material_ON = 1


## Writes aerotech intro to final file (only runs if you flagged it as true)
def intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start):
    with open(intro_gcode, "r") as g:
        with open(export_gcode_txt, 'w') as f:
            for line in g:
                line = line.replace('{Z_var}', Z_var).replace('{ramprate}', str(ramprate)).replace('{feed}', str(feed)).replace('{Z_start}', str(Z_start))
                #line = line.replace('{com1}', str(com[0])).replace('{com2}', str(com[1]))
                f.write(line)
        g.close()

    return f
    f.close()

if intro_flag == True:
    intro_export = intro(intro_gcode, export_gcode_txt, Z_var, ramprate, feed, Z_start)
    type_open = "a"
else:
    type_open = "w"


## generates the g-code
with open(export_gcode_txt, type_open) as f:
    f.write("\n\r;------------Set Pressures------------")
    f.write(setpress1)
    f.write(setpress2)
    f.write(toggleON_1)
    # for repeat in range(3):
    #     f.write("\nG1 X3")
    #     f.write(toggleON_2)
    #     f.write(toggleOFF_1)
    #
    #     f.write("\nG1 X3")
    #     f.write(toggleON_1)
    #     f.write(valveOFF_2)

    f.write("\nG1 X" + str(offset*2))# + str(offset))
    for i in range(number_lines_to_print):
        current_line = i + 1
        new_line = True
        if i > 1:
            f.write("\n;------------- new line -------------------")

        ############ defining the x-movements; i.e., is it moving + or -, are there G0 moves, are there offset
        if current_line % 2 != 0:  ## odd line
            move_x_1 = move_pos_x
            move_x_code_offset_1 = move_pos_x_offset
            move_x_final_col_1 = move_pos_x_end_line#"\nG1 X" + str(x)
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
            move_x_final_col_1 = move_neg_x_end_line#"\nG1 X" + str(-x)
            move_x_2 = move_x_1
            move_x_code_offset_2 = move_x_code_offset_1
            move_x_final_col_2 = move_x_final_col_1

            if G0_moves == True:
                move_x_2 = "\nG0" + _X
                move_x_code_offset_2 = "\nG0 X" + str(-offset)
                move_x_final_col_2 = "\nG0 X" + str(-x)

        ############ deterning what material to turn on or off
        if current_line <= lines_per_row * row_count:
            for j in range(col):
                if j > 0:
                    new_line = False
                if (j + 1) == col:  ## if the last column
                    if material_ON == 1:
                        move_x_code = move_x_final_col_1
                        move_x_code_offset = '\r'
                        switchOFF = toggleOFF_1
                        switchON = toggleON_1
                    elif material_ON == 2:
                        move_x_code = move_x_final_col_2
                        move_x_code_offset = '\r'
                        switchOFF = toggleOFF_2
                        switchON = toggleON_2

                    switch = switchOFF + move_pos_y_offset + switchON  + move_pos_y_remain ### to turn material off during y-moves
                    if y_move_ON == True:
                        switch = '\n' + move_pos_y  ### to keep material on during y-moves

                    if current_line == number_lines_to_print:  ## if the last column and the end of the print
                        if material_ON == 1:
                            switch = toggleOFF_1
                        elif material_ON == 2:
                            switch = toggleOFF_2

                elif material_ON == 1:
                    move_x_code = move_x_1
                    move_x_code_offset = move_x_code_offset_1
                    switch = toggleON_2 + toggleOFF_1
                    material_ON = 2
                elif material_ON == 2:
                    move_x_code = move_x_2
                    move_x_code_offset = move_x_code_offset_2
                    switch = toggleON_1 + toggleOFF_2
                    material_ON = 1

                ############ actually writing the code to the text file... finally
                if new_line == True and apply_offset == True:
                    print("true")
                    f.write(move_x_code_offset)
                else:
                    f.write(move_x_code)
                f.write('\n;--------------')
                f.write(switch)
                # if apply_offset == True:
                #     f.write(move_x_code_offset)

            ############ determines what to do on the last lines of each row
            if current_line == lines_per_row * row_count and current_line != number_lines_to_print:  ## if the last line of the row and not the last line in the print
                f.write("\r\n;--------------------------------- new row --------------------------------")
                if material_ON == 1:  # switching from odd rows to even row
                    switch = toggleON_2 + toggleOFF_1
                    material_ON = 2
                else:
                    switch = toggleON_1 + toggleOFF_2
                    material_ON = 1
                f.write(switch)
                row_count += 1  ## moves loop to next row block

## Writes aerotech ending to final file (only runs if you flagged it as true)
def ending(ending_gcode, export_gcode_txt, Z_var):
    with open(ending_gcode, "r") as g:
        with open(export_gcode_txt, 'a') as f:
            f.write('\n\r')
            for line in g:
                line = line.replace('{file_name1}', file_name[0]).replace('{file_name2}', file_name[1]).replace(
                    '{Z_var}', Z_var).replace('{ramprate}', str(ramprate)).replace('{feed}', str(feed)).replace(
                    '{Z_start}', str(Z_start))
                line = line.replace('{com1}', str(com[0])).replace('{com2}', str(com[1]))
                f.write(line)

        g.close()

    return f
    f.close()
if ending_flag == True:
    ending_export = ending(ending_gcode, export_gcode_txt, Z_var)

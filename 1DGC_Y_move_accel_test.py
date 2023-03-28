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
# Desired XYZ motion
x = 5
y = 0.2
z = 0.58 #1  # 0.58
Z_var = "Z"

length = 180 # mm
pressure = [50, 40]
num_lines_to_test = 1000
######################################################################################################################

com = ["serialPort1", "serialPort2"]

# setpress1 = "\n"
# toggleON_1 = "\n"
# toggleOFF_1 = "\n"

setpress1 = str('\n\r'+com[0] +'.write('  + str(setpress(pressure[0])) + ')') # material 1
toggleON = str('\n\r'+com[0] +'.write('  + str(togglepress()) + ')') # turn on material 2
toggleOFF = toggleON

## Defined XYZ (don't change
X = " X" + str(x)
Y = " Y" + str(y)
Z = " " + Z_var + str(z)

_X = " X" + str(-x)
_Y = " Y" + str(-y)
_Z = " " + Z_var + str(-z)

move_pos_x = "\nG1" + X
move_neg_x = "\nG1" + _X
move_pos_y = "\n\rG1" + Y + "\n\r"
move_neg_y = "\n\rG1" + _Y + "\n\r"


num_lines = int(length/y)

print(num_lines)
if num_lines%2 == 0:
    num_lines += 1
print(num_lines)
print("length = ", num_lines_to_test*y)
with open("1DGC_Y_move_accel_test_gcode.txt", "w") as f:
    f.write(setpress1)
    #f.write("\n\rG1 Y" + str(-length))
    while num_lines_to_test > 0:
        f.write(toggleON)
        print("toggleON_1")
        print("num_lines_to_test_A = ", num_lines_to_test)
        f.write("\r\n;------------------- New Column (ODD) -------------------")
        if num_lines_to_test < num_lines:
            num_lines = num_lines_to_test
        f.write("\r\n;-----number of lines: " + str(num_lines) + "-----")
        for i in range(num_lines):
            if (i+1) == num_lines:
                if (num_lines % 2 != 0):
                    move_x = move_pos_x
                    shift = '\r\nG1 X1'
                else:
                    move_x = move_neg_x
                    shift = '\r\nG1 X-1'
                f.write("\r\n;----Last line----")
                f.write(move_x)
                f.write(toggleON)
                print("toggleON_1")
                f.write(move_x + shift)
                num_lines_to_test -= 1

                if num_lines_to_test == 0:
                    f.write(toggleOFF)
                    print("toggleOFF_1")

                num_lines_to_test -= 1
            elif (i+1)%2 != 0: # odd lines
                f.write("\r\n;----ODD line----")
                f.write(move_pos_x)
                f.write(toggleOFF)
                print("toggleOFF_1")
                f.write(move_pos_x)
                num_lines_to_test -= 1
            else: # even lines
                f.write(move_pos_y)
                f.write("\r\n;---- EVEN line----")
                f.write(move_neg_x)
                f.write(toggleON)
                print("toggleON_1")
                f.write(move_neg_x)
                f.write(move_pos_y)
                num_lines_to_test -= 1

        print("num_lines_to_test_B = ", num_lines_to_test)
        if num_lines_to_test < num_lines:
            num_lines = num_lines_to_test

        f.write("\r\n;------------------- New Column (Even) -------------------")
        f.write("\r\n;-----number of lines: " + str(num_lines) + "-----")

        # if num_lines_to_test>0:
        #     f.write(toggleON)
        #     print("toggleON_1")

        for i in range(num_lines):
            if (i + 1) == num_lines:
                if (num_lines % 2 != 0):
                    move_x = move_pos_x
                    shift = '\r\nG1 X1'

                else:
                    move_x = move_neg_x
                    shift = '\r\nG1 X-1'

                f.write("\r\n;----Last line----")
                f.write(move_x)
                f.write(toggleON)
                print("toggleON_1")
                f.write(move_x + shift)

                num_lines_to_test -= 1

                if num_lines_to_test == 0:
                    f.write(toggleOFF)
                    print("toggleON_1")
            elif (i+1)%2 != 0: # odd lines
                f.write("\r\n;----ODD line----")
                f.write(move_pos_x)
                f.write(toggleOFF)
                print("toggleOFF_1")
                f.write(move_pos_x)
                num_lines_to_test -= 1
            else: # even lines
                f.write(move_neg_y)
                f.write("\r\n;----EVEN line----")
                f.write(move_neg_x)
                f.write(toggleON)
                print("toggleON_1")
                f.write(move_neg_x)
                f.write(move_neg_y)
                num_lines_to_test -= 1



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
y = 1
z = 0.58 #1  # 0.58
Z_var = "Z"

length_max = 180 # mm how big is the glass plate?
pressure = [66, 40]
num_lines_to_test = 500 # how many lines total do you want to test?

spacing = 3 # spacing between line used to measure stopping point and start of snake
tail_y = 10 # distance printer should move after the material is toggled off
######################################################################################################################

com = ["serialPort1", "serialPort2"]

# setpress1 = "\n"
# toggleON = "\n"
# toggleOFF_1 = "\n"
#
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


num_lines = int(length_max / y) # number of lines that fit on one length of glass plate
new_length = num_lines*y # recalculated length so that it represents a multiple of an integar value
total_length = num_lines_to_test * y # total length that needs to be printed

print("num_lines = ", num_lines)
print("new_length = ", new_length)
print("total_length = ", total_length)

with open("Y_move_test_continuous_gcode.txt", "w") as f:
    if num_lines_to_test <= num_lines:
        num_lines = num_lines_to_test
        new_length = total_length

    f.write(setpress1)
    f.write(toggleON)

    f.write('\n\rG1 Y' + str(-new_length))
    f.write('\n\rG1 X' + str(x))

    while num_lines_to_test > 0:

        f.write('\n\rG1 Y' + str(new_length))
        f.write('\n\rG1 X' + str(spacing))
        for i in range(num_lines):
            if (i+1)%2 != 0: #odd rows
                f.write(move_pos_x)
            else:
                f.write(move_neg_x)

            f.write(move_neg_y)
            num_lines_to_test -= 1

        if num_lines_to_test <= num_lines:
            num_lines = num_lines_to_test

        if num_lines_to_test != 0:
            f.write('\n\rG1 X' + str(x+spacing))
            new_length = (num_lines*y)

        else:
            f.write(toggleOFF)
            # f.write('\n\rG1 Y' + str(-tail_y))










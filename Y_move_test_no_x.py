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
x = 0.6
y = x
z = 0.58 #1  # 0.58
Z_var = "Z"

length_max = 160 # mm how big is the glass plate?
pressure = [68, 40]
num_lines_to_test_OG = 500 # how many lines total do you want to test?

spacing = 3 # spacing between line used to measure stopping point and start of snake
tail_y = 80 # distance printer should move after the material is toggled off
######################################################################################################################
############################ AEROTECH INPUTS #############################################
feed = 25 # feedrate mm/s
accel = 1000#700 # mm/s^2
decel = -1000#-700 # mm/s^2

offset = 0#-2#0  #use a negative number to increase length of time/material being on (units in mm)
start_delay = 0#3.5 #(units in mm)

Z_var = "D"
z_height = 0.4
z_o= -150 + z_height

home = False  #do you want to home it? (True = yes)

# Open the port for the python-hyrel connection
port_aerotech = 1 #port named in python code to connect to aerotech
port_python = 2 #this port is named in aerotech code to connect to python


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

num_lines_to_test = num_lines_to_test_OG

num_lines_OG = int(length_max / y) # number of lines that fit on one length of glass plate
num_lines = num_lines_OG

new_length_OG = num_lines*y # recalculated length so that it represents a multiple of an integar value
new_length = new_length_OG

total_length_OG = num_lines_to_test * y # total length that needs to be printed
total_length = total_length_OG

print("num_lines = ", num_lines)
print("new_length = ", new_length)
print("total_length = ", total_length)

with open("Y_move_test_no_x_gcode.txt", "w") as f:
    if num_lines_to_test <= num_lines:
        num_lines = num_lines_to_test
        new_length = total_length

    f.write(setpress1)
    f.write(toggleON)

    f.write('\n\rG1 Y' + str(-new_length))
    f.write('\n\rG1 X' + str(spacing))

    while num_lines_to_test > 0:

        f.write('\n\rG1 Y' + str(new_length))
        # f.write(toggleOFF)
        f.write('\n\rG1 X' + str(spacing))
        # f.write(toggleON)
        for i in range(num_lines):
            if (i + 1) % 2 != 0:  # odd rows
                f.write(move_neg_y)
            else:
                f.write(move_neg_x)

            num_lines_to_test -= 1

        if num_lines_to_test <= num_lines:
            num_lines = num_lines_to_test

        if num_lines_to_test != 0:
            f.write('\n\rG1 X' + str(spacing))
            new_length = (num_lines*y)
        else:
            f.write(toggleOFF)
            # f.write('\n\rG1 Y' + str(-tail_y))
f.close()

with open("Y_move_test_no_x_aerotech.txt", "w") as f:
    f.write("DVAR $hFile\n\r")
    f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP TYPE LINEAR X Y \nRAMP RATE ' + str(
        accel) + '\n\rVELOCITY OFF\n\r')

    f.write("ENABLE X Y " + Z_var + "\n")
    if home == True:
        f.write("HOME X Y " + Z_var + "\r\n")
        f.write("'G90\n'G0 X0 Y0 " + Z_var + "0\n'G91\n\r")
    else:
        f.write("'HOME X Y " + Z_var + "\r\n")
        f.write("G90\nG0 X0 Y0 " + Z_var + "0\nG91\n\r")

    f.write(";Begin Motion\n")
    f.write("G0 X80 Y265  \n")
    f.write("G0 " + Z_var + str(z_o) + "\n")
    f.write("G1 F" + str(feed) + "\n\r")

    f.write("\n\rFILECLOSE")
    f.write('\n$hFile = FILEOPEN "COM' + str(port_python) + '", 2')
    f.write('\nCOMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"')
    f.write('\nCOMMSETTIMEOUT $hFile, -1, -1, 1000')
    f.write('\n\rFILEWRITE $hFile, "start1"')
    f.write('\nG4 P3\n\r')
f.close()


y_move = 0
num_lines_to_test = num_lines_to_test_OG # how many lines total do you want to test?
num_lines = num_lines_OG
new_length = new_length_OG
total_length = total_length_OG

with open("Y_move_test_no_x_aerotech.txt", "a") as f:
    if num_lines_to_test <= num_lines:
        num_lines = num_lines_to_test
        new_length = total_length

    f.write('\n\rG1 Y' + str(-new_length))
    f.write('\n\rG1 X' + str(spacing))

    while num_lines_to_test > 0:
        f.write('\n\rG1 Y' + str(new_length))
        f.write('\n\rG1 X' + str(spacing))
        for i in range(num_lines):
            f.write(move_neg_y)
            num_lines_to_test -= 1

        f.write('\n\rG1 Y'+ str(y_move))

        if num_lines_to_test <= num_lines:
            num_lines = num_lines_to_test

        if num_lines_to_test != 0:
            f.write('\n\rG1 X' + str(spacing))
            new_length = (num_lines * y)

        else:
            f.write('\n\rG1 Y' + str(-tail_y))

    f.write('\n\rFILECLOSE $hFile\nM02')





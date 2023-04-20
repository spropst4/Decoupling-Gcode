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

# path starts in the middle of the spiral.

export_gcode_txt = "1DGC_Generate_SemiSpiral_Cylinder_Switching_gcode.txt"
circle_diam_outer = 30
circle_diam_inner = 10
filament_width = 1.1
z = 1.2
Z_var = "Z"
Z_start = -150 + z

num_layers = 5
reverse = "G3" # Options: "G2" (reverse the spiral direction each layer) or "G3" continue in ccw direction

# Feedrate
feed = 20  # mm/sec
ramprate = 1000 # mm/s/s

pressure = [28, 28] # 1 is core, 2 is shell
com = [4, 5] #core 1, shell 2

## Are you applying offsets?
apply_offset = False
offset = 3.9                                 # 1.4  # for F=15 #2.5mm for F=25

## Apply intro?
intro_flag = False                             # mark True if you want to add an intro; mark False if you don't want to add an intro
ending_flag = False                              # mark True if you want to add an ending; mark False if you don't want to add an ending
intro_gcode = "Spropst_aerotech_intro.txt"
ending_gcode = "Spropst_aerotech_end.txt"

if apply_offset == False:
    offset = 0
com = ["serialPort1", "serialPort2"]

######################################################################################################################

setpress1 = str('\n\r' + com[0] + '.write(' + str(setpress(pressure[0])) + ')') # material 1
setpress2 = str('\n\r' + com[1] + '.write(' + str(setpress(pressure[1])) + ')') # material 2
# setpressCore = '\n\r Pressure Material 1'  # material 1
# setpressShell = '\n\r Pressure Material 2'  # material 2

toggleON_1 = str('\n\r' + com[0] + '.write(' + str(togglepress()) + ')') # turn on material 1
toggleOFF_1 = toggleON_1
# toggleON_Core = '\n\rMaterial 1 ON'
# toggleOFF_Core = '\n\rMaterial 1 OFF'

toggleON_2 = str('\n\r' + com[1] + '.write(' + str(togglepress()) + ')')  #start 2nd material
toggleOFF_2 = toggleON_2 #'\n'  # "\nM792 ;SEND Ultimus_IO["+str(comRight)+"]= 0" #stop 2nd material
# toggleON_Shell = '\n\rMaterial 2 ON'
# toggleOFF_Shell = '\n\rMaterial 2 OFF'
import numpy as np
Gcommand_list = []
X_list = []
Y_list = []
Z_list = []
I_list = []
J_list = []
Command_list = []

circle_diam = circle_diam_inner
if circle_diam_inner == 0:
    circle_diam = 2*filament_width

for l in range(num_layers):
    if l > 0:
        Gcommand_list.append("G1")
        Command_list.append(False)
        Z_list.append(z)
        X_list.append(0)
        I_list.append(0)
        Y_list.append(0)
        J_list.append(0)
    if (l+1)%2 != 0: #odd layers
        i = 0
        while circle_diam < circle_diam_outer:
            if i > 0:
                circle_diam += filament_width
            if (i + 1) % 2 != 0:  ## odd lines
                Gcommand_list.append("G3")
                X_list.append(-circle_diam)
                I_list.append(-circle_diam / 2)
                Y_list.append(0)
                Z_list.append(0)
                J_list.append(0)
                Command_list.append(True)
                odd = True

            else:
                Gcommand_list.append("G3")
                X_list.append(circle_diam)
                I_list.append((circle_diam) / 2)
                Y_list.append(0)
                Z_list.append(0)
                J_list.append(0)
                Command_list.append(True)
                odd = False

            i += 1

    else:  # even layers
        i = 0
        # Gcommand_list.append("G1")
        # Command_list.append(False)
        # Z_list.append(z)
        # X_list.append(0)
        # I_list.append(0)
        # Y_list.append(0)
        # J_list.append(0)

        while circle_diam > circle_diam_inner:
            if i > 0:
                circle_diam -= filament_width
            if (i + 1) % 2 != 0:  ## odd lines
                Gcommand_list.append(reverse)
                if odd == True:
                    X_list.append(circle_diam)
                    I_list.append(circle_diam / 2)
                else:
                    X_list.append(-circle_diam)
                    I_list.append(-circle_diam / 2)
                Y_list.append(0)
                Z_list.append(0)
                J_list.append(0)
                Command_list.append(True)

            else:
                Gcommand_list.append(reverse)
                if odd == True:
                    X_list.append(-circle_diam)
                    I_list.append(-circle_diam / 2)
                else:
                    X_list.append(circle_diam)
                    I_list.append(circle_diam / 2)
                Y_list.append(0)
                Z_list.append(0)
                J_list.append(0)
                Command_list.append(True)
            i += 1

print(Gcommand_list)
print(X_list)
print(Y_list)
print(Z_list)
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
    # f.write("\n\rG1 X"+str(circle_diam_outer) + " Y"+str(circle_diam_outer) )
    f.write(setpress1)
    f.write(setpress2)
    f.write(toggleON_1)
    #f.write(toggleON_2)
    M1_ON = True
    for i in range(len(Gcommand_list)):
        if Gcommand_list[i] == "G3" or Gcommand_list[i] == "G2":
            #Gcommand_list[i] = "CCW"
            if I_list[i] == 0 and J_list[i] == 0:
                f.write("\n\r")
            else:
                f.write("\n\r" + Gcommand_list[i] + " X" + str(X_list[i]) + " Y" + str(Y_list[i]) + " I" + str(I_list[i]) + " J" + str(J_list[i]))
        else:
            f.write("\n\r;------NEW LAYER_________________________")
            f.write("\n\r" + Gcommand_list[i] + " "+Z_var + str(Z_list[i]))

        if Command_list[i] == True:
            if (i+1) < len(Gcommand_list) and reverse == "G2" and Gcommand_list[i+1] == "G1":
                f.write("")
            elif M1_ON == True:
                f.write(toggleON_2)
                f.write(toggleOFF_1)
                M1_ON = False
                M2_ON = True
            else:
                f.write(toggleON_1)
                f.write(toggleOFF_2)
                M1_ON = True
                M2_ON = False

    if M1_ON == True:
        f.write(toggleOFF_1)
    if M2_ON == True:
        f.write(toggleOFF_2)
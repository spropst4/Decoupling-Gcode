def openport(port):
    # IMPORTS
    import serial
    baudrate = 115200
    bytesize = 8
    timeout = 2

    return serial.Serial("COM" + str(port), baudrate=baudrate, bytesize=bytesize, timeout=timeout, stopbits=serial.STOPBITS_ONE)
from datetime import datetime
from datetime import date
now = datetime.now() # datetime object containing current date and time
current_date = date.today()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")     # dd/mm/YY H:M:S
############################## INPUTS ####################################
import math
import numpy as np
from math import sqrt
import time

# Open the ports for the pressure box
press_com1 = 5 # core
press_com2 = 4 # shell

serialPort1 = openport(press_com1)
serialPort2 = openport(press_com2)

############################## PASTE ####################################

#date and time: 24/03/2023 14:47:04
feed = 25
accel = 1000
decel = -1000
testing =  "y = 1, feed = 25 mm/s, accel = 1000 mm/s^2"
gcode_txt_imported = "Y_move_test_continuous_gcode.txt"
final_gcode_txt_export = "Y_move_test_continuous_aerotech.txt"
start_delay_time = 0.0
offset_time = 0.0
set_press = "[serialPort1.write(b'\x05\x02\x30\x38\x50\x53\x20\x20\x30\x36\x36\x30\x45\x39\x03')]"
initial_toggle = "[serialPort1.write(b'\x05\x02\x30\x34\x44\x49\x20\x20\x43\x46\x03')]"
time_based_dict_final = {0: 173.575000000006}
command_dict_final = {0: "[serialPort1.write(b'\\x05\\x02\\x30\\x34\\x44\\x49\\x20\\x20\\x43\\x46\\x03')]"}

Z_var = "D"
z_height = 0.2
z_o= -150 + z_height

home = False  #do you want to home it? (True = yes)

# Open the port for the python-hyrel connection
port_aerotech = 1 #port named in python code to connect to aerotech
port_python = 2 #this port is named in aerotech code to connect to python

## open and read in gcode txt file into a list - remove comments, spaces, random characters
def open_gcode(gcode_txt):
    gcode_list = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            gcode_list.append(myline.strip('\n'))
        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        #gcode_list = [x for x in gcode_list if ";" not in x] # removes comments
        gcode_list = [x for x in gcode_list if ";-" not in x]  # removes comments
        # print('Original: ', gcode_list)
        gcode.close()
        return gcode_list
gcode_list = open_gcode(gcode_txt_imported)

## splits up gcode into directions, distances, G command type (G1, G2, G3, etc)
## create a gcode,  distance, and direction dictionary
parse_start = time.time()
def parse_gcode(gcode_list):
    ## find specific characters in a string
    def find(s, ch):  # s = string to search, ch = character to find
        # s = a string
        # ch = character to find
        return [i for i, ltr in enumerate(s) if ltr == ch]

    ## pythagoream thm
    def pythag(x, y):
        return (sqrt(abs(float(x)) ** 2 + abs(float(y)) ** 2))

    ## find arc_angle
    def arc_angle(X, Y, I, J):
        dx = X - I
        dy = Y - J
        angle = np.atan2(dy, dx)
        if angle < 0:
            angle = (np.pi * 2) + angle
        return angle

    X_index = {}
    Y_index = {}
    Z_index = {}
    distance_commands_dict = {}
    gcode_dict = {}
    direction_dict = {}
    g_command_dict = {}
    direction_list = []
    distance_list = []
    g_command_list = []
    for i in range(len(gcode_list)):
        gcode_dict[i] = gcode_list[i].split(" ")
        find_x = find(gcode_list[i], "X")
        find_y = find(gcode_list[i], "Y")
        find_z = find(gcode_list[i], "Z")
        X_index[i] = find_x
        Y_index[i] = find_y
        Z_index[i] = find_z
        if 'G1' in gcode_dict[i]:
            g_command_dict[i] = 'G1'
            g_command_list.append('G1')
            if X_index[i] != [] and Y_index[i] != []:
                x = gcode_dict[i][1].strip("X")
                y = gcode_dict[i][2].strip("Y")
                distance_commands_dict[i] = pythag(x, y)
                direction_dict[i] = "Y/X" + str(float(y) / float(x))
                distance_list.append(distance_commands_dict[i])
                direction_list.append(direction_dict[i])

            if X_index[i] != [] and Y_index[i] == []:
                distance = gcode_dict[i][1].strip("X").strip("Y")
                distance_commands_dict[i] = float(distance)
                direction_dict[i] = "X"
                distance_list.append(distance_commands_dict[i])
                direction_list.append(direction_dict[i])

            if X_index[i] == [] and Y_index[i] != []:
                distance = gcode_dict[i][1].strip("X").strip("Y")
                distance_commands_dict[i] = float(distance)
                direction_dict[i] = "Y"
                distance_list.append(distance_commands_dict[i])
                direction_list.append(direction_dict[i])

            if X_index[i] == [] and Y_index[i] == [] and Z_index[i] != []:
                distance = gcode_dict[i][1].strip("X").strip("Y").strip("Z")
                distance_commands_dict[i] = float(distance)
                direction_dict[i] = "Z"
                distance_list.append(distance_commands_dict[i])
                direction_list.append(direction_dict[i])

        else:
            distance_commands_dict[i] = gcode_dict[i][0]

        if 'G3' in gcode_dict[i]:
            x = gcode_dict[i][1].strip("X")
            y = gcode_dict[i][2].strip("Y")
            I = gcode_dict[i][3].strip("I")
            J = gcode_dict[i][4].strip("J")
            R = pythag(I, J)

    # print("X_index = ", X_index)
    # print("Y_index = ", Y_index)

    # print("gcode_dict = ", gcode_dict)  # don't use outside of this function...
    # print("distance_commands_dict = ", distance_commands_dict)
    # print("direction_dict = ", direction_dict)  # don't use outside of this function
    # print("g_command_dict = ", g_command_dict)  # don't use outside of this function
    # print("distance_list = ", distance_list)
    # print("direction_list = ", direction_list)
    # print("g_command_list = ", g_command_list)

    return distance_commands_dict, distance_list, direction_list, g_command_list
parsed_gcode = parse_gcode(gcode_list)
distance_commands_dict = parsed_gcode[0] #contains both distances and commands
distance_list = parsed_gcode[1] # contains the distances
direction_list = parsed_gcode[2] # contains the directions, i.e., X, Y, Y/X (diagonal)
g_command_list = parsed_gcode[3] # contains the G commands
parse_end = time.time()
print("Build time:  parse_gcode = ", parse_end - parse_start)

condense_start = time.time()

## creates simplified gcode for 3d printer and for use in acceleration profile
def condense_gcode(distance_list, final_gcode,  dt_string, testing):
    sum_distance = distance_list[0]
    current_direction = direction_list[0]
    current_g_command = g_command_list[0]
    current_gcode = current_direction + str(sum_distance)

    sum_dist_list = [sum_distance]
    sum_dir_list = [current_direction]
    sum_g_list = [current_g_command]
    sum_gcode_list = [current_gcode]

    group_dist_accel_dict = {}
    group_abs_dist_accel_dict = {}
    group_dist_list = [sum_distance]
    group_sum_dist_list = [sum_distance]

    count = 0
    for i in range(1,len(distance_list)):
        if direction_list[i] == direction_list[i-1]:
            sum_distance += distance_list[i]
            count = count
            sum_dist_list[count] = sum_distance
            current_direction = direction_list[i]
            current_g_command = g_command_list[i]
            sum_dir_list[count] = current_direction
            sum_g_list[count] = current_g_command
            sum_gcode_list[count] = (current_direction + str(sum_distance))
            group_dist_list.append(distance_list[i])
            group_sum_dist_list.append(sum_distance)

        else:
            count += 1
            group_dist_list = []
            group_sum_dist_list = []
            sum_distance = distance_list[i]
            current_direction = direction_list[i]
            current_g_command = g_command_list[i]
            sum_dist_list.append(sum_distance)
            sum_dir_list.append(current_direction)
            sum_g_list.append(current_g_command)
            sum_gcode_list.append(current_direction + str(sum_distance))
            group_dist_list.append(distance_list[i])
            group_sum_dist_list.append(sum_distance)

        group_dist_accel_dict[count] = group_dist_list
        group_abs_dist_accel_dict[count] = group_sum_dist_list

    # print("sum_dist_list = ", sum_dist_list)
    # print("sum_dir_list = ", sum_dir_list)
    # print("sum_g_list = ", sum_g_list)
    # print("sum_gcode_list = ", sum_gcode_list)
    # print("group_dist_accel_dict = ", group_dist_accel_dict)
    # print("group_abs_dist_accel_dict = ", group_abs_dist_accel_dict)

    ## create txt for gcode used in 3d printer
    with open(final_gcode, "w") as f:
        f.write("' date: " + dt_string)
        f.write('\r'  + final_gcode)
        f.write("\r' "+ testing)
        f.write("\n\rDVAR $hFile\n\r")
        f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP TYPE LINEAR X Y \nRAMP RATE ' +str(accel)+ '\n\rVELOCITY OFF\n\r')

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
        f.write('\n$hFile = FILEOPEN "COM'+str(port_python) +'", 2')
        f.write('\nCOMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"')
        f.write('\nCOMMSETTIMEOUT $hFile, -1, -1, 1000')
        f.write('\n\rFILEWRITE $hFile, "start1"')
        f.write('\nG4 P3\n\r')

        for i in range(len(sum_gcode_list)):
            coord = sum_gcode_list[i]
            G_command = sum_g_list[i]
            f.write( G_command + " " + coord + "\r\n")

        f.write('\n\rG1 Y-10')
        f.write('\n\rFILECLOSE $hFile\nM02')

    return sum_dist_list, f
sum_dist_list = condense_gcode(distance_list, final_gcode_txt_export, dt_string, testing)[0] # creates list of distance where each entry represents a new acceleration profile
condense_end = time.time()
print("Build time:  condense_gcode = ", condense_end - condense_start)

###### WAITING FOR PING ##################################
print("\nWaiting for ping to start....")
if __name__ == '__main__':

    ser = openport(port_aerotech)
    ser.reset_input_buffer()

    told = time.time()
    intervals = []

    count = 0
    while True:
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            print('\r\n------------------')
            message = ser.read(bytesToRead)  # creates type bytes, e.g., b'M792 ;SEND message\n'
            message = message.decode(encoding='utf-8')  # creates type string, e.g., 'M792 ;SEND message\n'
            print('Received command: ' + message)
            if message == "start1\r\n":
                pause = 0.011305268287658692 #from AEROTECH_PING_data.txt

                exec(set_press)
                print("Setting the pressures....")

                break

#### Executes Absolute timing ####
print("Executing time-based code....")
time.sleep(3-pause-start_delay_time)

i = 0
exec(initial_toggle)
print("Initial toggle....")

start_time = time.time()
# time_dict_list = []
# error_list = []
# real_time_list = []
while (i < len(command_dict_final)):
    current_time_stamp = time_based_dict_final[i] - offset_time
    real_time = time.time() - start_time
    if (real_time >= (current_time_stamp)):
        exec(command_dict_final[i])
        # error = float(real_time - current_time_stamp)
        print("Time: ", real_time)
        print("\tCommands: ", command_dict_final[i])
        # print("\tError: ",(error))
        # if time_based_dict_final[i] != 0:
        #     time_dict_list.append(current_time_stamp)
        #     real_time_list.append(real_time)
        #     error_list.append(error)
        i += 1
print("DONE!")

serialPort1.close()
serialPort2.close()

# avg_error = np.average(error_list)
# std_error = np.std(error_list)
#
# print("avg_error = ", avg_error)
# print("std_error = ", std_error)
#
# from datetime import date
# current_date = date.today()
#
# with open(str(current_date) + "_Time_error.txt", "a") as f:
#     from datetime import datetime
#     now = datetime.now() # datetime object containing current date and time
#     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")     # dd/mm/YY H:M:S
#     f.write('\r\n----------------------------')
#     f.write('\r\ndate and time: ' + dt_string)
#     f.write('\rgcode used: ' + gcode_txt_imported)
#     f.write('\rTesting: ' + testing)
#     f.write('\rnum_points = ' + str(len(error_list)))
#     f.write("\rerror_list = " + str(error_list))
#     f.write("\ravg_error = " + str(avg_error))
#     f.write("\rstd_error = " + str(std_error))
#
#
# with open(str(current_date) + "_Real_time_plt.py", "a") as f:
#     from datetime import datetime
#     now = datetime.now() # datetime object containing current date and time
#     dt_string = now.strftime("%d/%m/%Y %H:%M:%S")     # dd/mm/YY H:M:S
#     f.write('\r\n#----------------------------')
#     f.write('\r\n#date and time: ' + dt_string)
#     f.write('\r#gcode used: ' + gcode_txt_imported)
#     f.write('\r#Testing: ' + testing)
#     f.write('\rnum_points = ' + str(len(time_based_dict_final)))
#     f.write("\rtime_dict = " + str(time_based_dict_final) + " #does not include offsets and delays")
#     f.write("\rtime_list = " + str(time_dict_list) + " #includes offsets and delays")
#     f.write("\rreal_time_list = " + str(real_time_list))
#     f.write('\rerror_list = ' + str(error_list))




# for i in range(len(command_dict_final)):
#     print("if time = ", time_based_dict_final[i])
#     print("\t\texecute: ", command_dict_final[i])
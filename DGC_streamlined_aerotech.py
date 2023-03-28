
def openport(port):
    # IMPORTS
    import serial
    baudrate = 115200
    bytesize = 8
    timeout = 2

    return serial.Serial("COM" + str(port), baudrate=baudrate, bytesize=bytesize, timeout=timeout, stopbits=serial.STOPBITS_ONE)

import time
import serial

############################## INPUTS ####################################
import math
import numpy as np
from math import sqrt

start_time = time.time()
yes = 0
no = 1
############################ INPUTS #############################################
feed = 25
# feedrate mm/s
accel = 1000#700 # mm/s^2
decel = -1000#-700 # mm/s^2

offset = 0 #-1 #-1 #-1#-1.5#-2 # use a negative number to increase length of time/material being on (units in mm)
start_delay = 0#5 #0#0.21389 #0#0.3 #0.21389 #0.27389 #0.29389 #0.25389 #0.21389 #0.3 #0.27 #0.3 # seconds (units in mm)
gcode_txt_imported ="1Output_Gcode_checker_BOTH.txt" #"1Output_Gcode_checker_CoreShell.txt" #"1Output_Gcode_checker_M1.txt"
final_gcode_txt_export = "2Output_Final_gcode_aerotech.txt"

number_of_ports_used = 2 # (aka number of materials used)

Z_var = "C"
z_height = 1.2
z_o= -150 + z_height

home = yes #do you want to home it?

# Open the ports for the pressure box
press_com1 = 4 # core
press_com2 = 5 # shell

serialPort1 = openport(press_com1)
serialPort2 = openport(press_com2)

# Open the port for the python-hyrel connection
port_aerotech = 1 #port named in python code to connect to aerotech
port_python = 2 #port named in aerotech code to connect to python

#########################################################################

print("Feedrate = ", feed, "mm/s")
print("Acceleration = ", accel, "mm/s^2", "\nDeceleration = ", decel, "mm/s^2")
print("Pressure Box Ports: COM", press_com1, " and COM", press_com2)
print("Python-Hyrel Port: COM", port_python)

print("\r\nImporting Gcode....")

## open and read in gcode txt file into a list - remove comments, spaces, random characters
def open_gcode(gcode_txt):
    gcode_list = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            gcode_list.append(myline.strip('\n'))
        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        #gcode_list = [x for x in gcode_list if ";" not in x] # removes comments
        gcode_list = [x for x in gcode_list if ";-" not in x]  # removes comments
        #print('Original: ', gcode_list)
        gcode.close()
        return gcode_list
gcode_list = open_gcode(gcode_txt_imported)

print("Translating Gcode to Time....")

## splits up gcode into directions, distances, G command type (G1, G2, G3, etc)
## create a gcode,  distance, and direction dictionary
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

## creates simplified gcode for 3d printer and for use in acceleration profile
def condense_gcode(distance_list, final_gcode):
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
        f.write("DVAR $hFile\n\r")
        f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP RATE ' +str(accel)+ '\n\r')

        f.write("ENABLE X Y " + Z_var + "\n")
        if home == yes:
            f.write("HOME X Y " + Z_var + "\r\n")
            f.write("'G90\n'G0 X0 Y0 " + Z_var + "0\n'G91\n\r")
        else:
            f.write("'HOME X Y " + Z_var + "\r\n")
            f.write("G90\nG0 X0 Y0 " + Z_var + "0\n'G91\n\r")

        f.write(";Begin Motion\n")
        f.write("G0 X150 Y50 \n")
        f.write("G0 " + Z_var + str(z_o) + "\n")
        f.write("G1 F" + str(feed) + "\n\r")

        f.write("\n\rFILECLOSE")
        f.write('\n$hFile = FILEOPEN "COM'+str(port_python) +'", 2')
        f.write('\nCOMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"')
        f.write('\nCOMMSETTIMEOUT $hFile, -1, -1, 1000')
        f.write('\n\rFILEWRITE $hFile, "start1"')
        f.write('\nG4 P2\nFILEWRITE $hFile, "start2"\nG4 P3\n\r')

        for i in range(len(sum_gcode_list)):
            coord = sum_gcode_list[i]
            G_command = sum_g_list[i]
            f.write( G_command + " " + coord + "\r\n")
        f.write('\n\rFILECLOSE $hFile\nM02')

    return sum_dist_list, f
sum_dist_list = condense_gcode(distance_list, final_gcode_txt_export)[0] # creates list of distance where each entry represents a new acceleration profile

## creates acceleration profile
def accel_profile(sum_dist_list):
    ## acceleration: find distance/time it takes to get to steady state velocity
    # def accel_length(v_0, v_f, accel):
    #     import sympy
    #     from sympy import symbols, solve
    #     # v_0 = starting velocity
    #     # max_v = desired feedrate #mm/s
    #     # accel = acceleration/ramprate
    #     x = symbols('x')
    #     t = symbols('t')
    #     v = symbols('v')
    #     sol_x = (v_f**2 - v_0**2)/(2*accel)
    #     x_steady = sol_x
    #
    #     sol_t = (v_f - v_0)/accel
    #     t_steady = sol_t
    #
    #     return x_steady, t_steady
    def accel_length(v_0, v_f, accel):
        import sympy
        from sympy import symbols, solve
        # v_0 = starting velocity
        # max_v = desired feedrate #mm/s
        # accel = acceleration/ramprate
        x = symbols('x')
        t = symbols('t')
        v = symbols('v')
        find_x = v_0 ** 2 + 2 * accel * x - v_f ** 2  # finds distance to steady state velocity
        sol_x = solve(find_x)
        for i in range(len(sol_x)):
            try:
                sol_x[i] >= 0
                check = 1
            except TypeError:
                check = 0
            if check == 1:
                x_steady = sol_x[i]

        find_t = v_0 + accel * t - v_f  # finds time to steady state velocity
        sol_t = solve(find_t)
        t_steady = sol_t[0]

        # print("distance to steady state: ", float(x_steady))
        return x_steady, t_steady
    accel_dist_dict = {}
    accel_time_dict = {}
    accel_dist_abs_dict = {}
    # accel_time_abs_dict = {}
    third = 0
    # third_t = 0
    for i in range(len(sum_dist_list)):
        if accel > 0:
            accel_dist = accel_length(0, feed, accel)[0]  # accel distance
            decel_dist = accel_length(feed, 0, decel)[0]  # decel distance
            accel_time = accel_length(0, feed, accel)[1]  # accel time
            decel_time = accel_length(feed, 0, decel)[1]  # decel time
            steady_state_dist = abs(sum_dist_list[i]) - accel_dist - decel_dist
        else:
            steady_state_dist = abs(sum_dist_list[i])
            accel_dist = 0
            decel_dist = 0
            accel_time = 0
            decel_time = 0

        if steady_state_dist <= 0:
            steady_state_dist = 0
            accel_dist = sum_dist_list[i]*0.5
            decel_dist = accel_dist
            accel_time = findt(0, accel, accel_dist)
            decel_time = findt(feed, decel, decel_dist)

        steady_state_time = steady_state_dist/feed
        accel_dist_dict[i] = [accel_dist, steady_state_dist, decel_dist]
        accel_time_dict[i] = [accel_time,steady_state_time, decel_time]

        prev_third = third
        first = prev_third + accel_dist
        second = first + steady_state_dist
        third = second + decel_dist

        accel_dist_abs_dict[i] = [first, second, third]

        # prev_third_t = third_t
        # first_t = prev_third_t + accel_time
        # second_t = first_t + steady_state_time
        # third_t = second_t + decel_time
        #
        # accel_time_abs_dict[i] = [first_t, second_t, third_t]

    # print("accel_dist_dict = ", accel_dist_dict)
    # print("accel_time_dict = ", accel_time_dict) # used in time-based function
    # print("accel_dist_abs_dict = ", accel_dist_abs_dict) # used in time-based function
    # print("accel_time_abs_dict = ", accel_time_abs_dict) # never used
    return accel_dist_abs_dict, accel_time_dict
accel_profile_output = accel_profile(sum_dist_list)
accel_profile_distance = accel_profile_output[0]
accel_profile_time = accel_profile_output[1]

## creates dictionary of time and commands
def distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_dict):
    # def findt(v_0, accel, x):
    #     import numpy as np
    #     from sympy import symbols, solve
    #     # v_0 = starting velocity
    #     # accel = acceleration or deceleration
    #     # x = distance travelled
    #     # t = time travelled
    #     a = 0.5*accel
    #     b = v_0
    #     c = -x
    #     t1 = (-b + np.sqrt(b**2 - 4*a*c))/(2*a)
    #     t2 = (-b - np.sqrt(b**2 - 4*a*c))/(2*a)
    #     sol_t = [t1, t2]
    #     for i in range(len(sol_t)):
    #         try:
    #             sol_t[i] >= 0
    #             t = sol_t[i]
    #         except TypeError:
    #             check = 0
    #     return t

    def findt(v_0, accel, x):
        from sympy import symbols, solve
        # v_0 = starting velocity
        # accel = acceleration/ramprate
        # x = distance traveled
        t = symbols('t')

        find_t = v_0 * t + 0.5 * (accel) * t ** 2 - x  # finds time
        sol_t = solve(find_t)
        for i in range(len(sol_t)):
            try:
                sol_t[i] >= 0
                t = sol_t[i]
            except TypeError:
                check = 0
        return t
    time_list = []
    time_dict = {}
    true = 0
    false = 1
    x_current = 0
    t = 0
    distance = 0
    partial_move = true
    for j in range(len(distance_dict)):
        if type(distance_dict[j]) != str:
            distance += abs(distance_dict[j])
            for i in range(len(accel_profile_distance)):
                accel_region = accel_profile_distance[i][0]
                max_velocity_region = accel_profile_distance[i][1]
                decel_region = accel_profile_distance[i][2]
                if distance >= accel_region:
                    t_current = accel_profile_time[i][0]
                    x_current = accel_region
                    t += t_current
                    #partial_move = true

                if distance >= max_velocity_region:
                    t_current = accel_profile_time[i][1]
                    x_current = max_velocity_region
                    t += t_current
                    #partial_move = true

                if distance >= decel_region:
                    t_current = accel_profile_time[i][2]
                    x_current = decel_region
                    t += t_current
                    #partial_move = true

                if partial_move == true:
                    if distance < accel_region:
                        relative_distance = distance - x_current
                        t_current = findt(0, accel, relative_distance)
                        t += t_current

                    elif distance < max_velocity_region:
                        relative_distance = distance - x_current
                        t_current = relative_distance/feed #findt(feed, 0, relative_distance)
                        t += t_current

                    elif distance < decel_region:
                        relative_distance = distance - x_current
                        t_current = findt(feed, decel, relative_distance)
                        t += t_current

                    partial_move = false

            time_output = t
            time_list.append(time_output)
            time_dict[j] = time_output
            t = 0
        else:
            time_dict[j] = distance_dict[j]

    return time_dict
time_dict = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_commands_dict )


delay_offset = [start_delay, abs(offset)]

start_delay_time = offset_time = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, delay_offset)[0]
offset_time = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, delay_offset)[1]
if offset < 0:
    offset_time = -offset_time

print("start_delay_time = ", start_delay_time, "\noffset_time = ", offset_time)

## creates final dictionaries of commands and times to use
def final_dicts(time_dict):
    command_list = []
    time_based_dict_final = {}
    command_dict_final = {}

    count_t = 0
    dict_count_t = 0
    start_count_c = 0
    initial_commands = []
    initial_commands_trigger = 0
    for i in range(len(time_dict)):
        entry = time_dict[i]
        dict_count_c = dict_count_t
        if type(entry) != str:
            time_based_dict_final[dict_count_t] = entry
            command_list = []
            count_t += 1
            start_count_c = 0
            initial_commands_trigger = 1
        else:
            command_list.append(entry)
            if initial_commands_trigger == 0:
                initial_commands = command_list
            else:
                command_dict_final[dict_count_c] = command_list
                if start_count_c == 0:
                    dict_count_t += 1
                    start_count_c = 1

    for i in range(len(command_dict_final)):
        command_list = command_dict_final[i]
        command_dict_final[i] = '[%s]' % ', '.join(map(str, command_list))

    # print("time_based_dict_unsummed = ", time_based_dict_unsummed)
    # print("time_based_dict_final = ", time_based_dict_final)
    # print("command_dict_final = ", command_dict_final)
    # print("initial_commands = ", initial_commands )
    return time_based_dict_final, command_dict_final, initial_commands
final_dicts_output = final_dicts(time_dict)
time_based_dict_final = final_dicts_output[0]
command_dict_final = final_dicts_output[1]
initial_commands = final_dicts_output[2]

set_press = '[%s]' % ', '.join(map(str,initial_commands[:number_of_ports_used]))
initial_toggle ='[%s]' % ', '.join(map(str, initial_commands[number_of_ports_used:]))

end_time = time.time()
total_time = end_time - start_time
print("\nTime to translate distance to time: ", total_time)

print("time_based_dict_final = ", time_based_dict_final)
print("set_press: ", set_press)
print("initial_toggle: ", initial_toggle)
print("command_dict_final = ", command_dict_final)
print("type in time_based_dict_final = ", type(time_based_dict_final[5]))
# prev = 0
# elem = time_based_dict_final[0]
# print(elem)
# for i in range(1,len(time_based_dict_final)):
#     time = time_based_dict_final[i] - time_based_dict_final[i-1]
#     print(time)
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
                pause = 0.011609828472137452
            # if message == "start1\r\n":
            #     tstart1 = time.time()

            # if message == "start2\r\n":
            #     tstart2 = time.time()
            #     delta = tstart2 - tstart1
            #     pause = 2 - delta

                exec(set_press)
                print("Setting the pressures....")

                break

# # ## Executes Absolute timing!!!!!!! NOTE: It starts after the
print("Executing time-based code....")
time.sleep(3-pause)
# if pause >= 0:
#     time.sleep(3 + 2*pause - start_delay)
# else:
#     time.sleep(3 + pause - start_delay)

i = 0
exec(initial_toggle)
start_time = time.time()
while (i < len(command_dict_final)):
    current_time_stamp = time_based_dict_final[i]
    command = command_dict_final[i]
    if i > 0:
       current_time_stamp = current_time_stamp - offset/feed
    if (time.time() - start_time >= (current_time_stamp) and i == i):
        print("Time: ", (time.time()-start_time))
        print("Commands: ", command)
        exec(command)
        i += 1
print("DONE!")

serialPort1.close()
serialPort2.close()

# for i in range(len(command_dict_final)):
#     print("if time = ", time_based_dict_final[i])
#     print("\t\texecute: ", command_dict_final[i])

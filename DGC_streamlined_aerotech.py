
def openport(port):
    # IMPORTS
    import serial
    baudrate = 115200
    bytesize = 8
    timeout = 2

    return serial.Serial("COM" + str(port), baudrate=baudrate, bytesize=bytesize, timeout=timeout, stopbits=serial.STOPBITS_ONE)



############################## INPUTS ####################################
import math
import numpy as np
from math import sqrt
import time

start_time = time.time()

############################ INPUTS #############################################
############################ INPUTS #############################################
feed = 25 # feedrate mm/s
accel = 1000#700 # mm/s^2
decel = -1000#-700 # mm/s^2

offset = 0#-2#0  #use a negative number to increase length of time/material being on (units in mm)
start_delay =0#3.5 #(units in mm)
gcode_txt_imported = "Y_move_accel_test_gcode.txt" #"1Output_Gcode_checker_M1.txt" #Y_move_accel_test_gcode.txt" #"1Output_Gcode_checker_M1.txt" #"1Output_Gcode_checker_CoreShell.txt" #"1Output_Gcode_checker_both.txt" #"1Output_Gcode_checker_M1.txt"
final_gcode_txt_export = "2Output_Final_gcode_aerotech.txt"
testing = "y = 2, feed = " +str(feed) + " mm/s, accel = " + str(accel) + " mm/s^2"

number_of_ports_used = 1 # (aka number of materials used)

Z_var = "C"
z_height = 0.52
z_o= -150 + z_height

home = False  #do you want to home it? (True = yes)

# Open the ports for the pressure box
press_com1 = 4 # core
press_com2 = 5 # shell

serialPort1 = openport(press_com1)
serialPort2 = openport(press_com2)

# Open the port for the python-hyrel connection
port_aerotech = 1 #port named in python code to connect to aerotech
port_python = 2 #this port is named in aerotech code to connect to python

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
print("length of parse_gcode = ", parse_end - parse_start)


condense_start = time.time()
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
        f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP TYPE LINEAR X Y \nRAMP RATE ' +str(accel)+ '\n\rVELOCITY OFF\n\r')

        f.write("ENABLE X Y " + Z_var + "\n")
        if home == True:
            f.write("HOME X Y " + Z_var + "\r\n")
            f.write("'G90\n'G0 X0 Y0 " + Z_var + "0\n'G91\n\r")
        else:
            f.write("'HOME X Y " + Z_var + "\r\n")
            f.write("G90\nG0 X0 Y0 " + Z_var + "0\nG91\n\r")

        f.write(";Begin Motion\n")
        f.write("G0 X150 Y50 \n")
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
        f.write('\n\rFILECLOSE $hFile\nM02')

    return sum_dist_list, f
sum_dist_list = condense_gcode(distance_list, final_gcode_txt_export)[0] # creates list of distance where each entry represents a new acceleration profile
condense_end = time.time()
print("length of condense_gcode = ", condense_end - condense_start)

accel_profile_start = time.time()
## creates acceleration profile
def accel_profile(sum_dist_list):
    import time
    def accel_length(v_0, v_f, accel):
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
                x_steady = sol_x[i]
                #x_steady = round(x_steady, 10)
            except TypeError:
                print("error in value of x; it may be imaginary")

        find_t = v_0 + accel * t - v_f  # finds time to steady state velocity
        sol_t = solve(find_t)
        t_steady = sol_t[0]
        #t_steady = round(t_steady, 10)
        return x_steady, t_steady
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
                #t = round(t, 10)
            except TypeError:
                print("error when calcuating time; might be getting an imaginary number.")
        return t
    def findv(v_0, accel, x):
        from sympy import symbols, solve
        # v_0 = starting velocity
        # accel = acceleration/ramprate
        # x = distance traveled
        # v = symbols('v')
        # find_v = v_0 ** 2 + 2 * accel * x - v ** 2
        # sol_v = solve(find_v)
        try:
            v = sqrt(v_0**2 + 2*accel*x)
            #v = round(v, 10)
        except TypeError:
            print("error when calcuating velocity; might be getting an imaginary number.")

        return v
        #return float(v)
    def findt_using_v(v_0, v_f, accel):
        t = (v_f - v_0)/accel
        #t = round(t, 10)
        return float(t)

    accel_dist_dict = {}
    accel_time_dict = {}
    accel_dist_abs_dict = {}
    accel_time_abs_dict = {}
    flag_accel_result = {}
    flag_decel_result = {}
    flag_short_move = {}
    decel_abs_dist = 0
    decel_abs_time = 0

    for i in range(len(sum_dist_list)):
        if accel == 0:
            steady_state_dist = abs(sum_dist_list[i])
            accel_dist = 0
            decel_dist = 0
            accel_time = 0
            decel_time = 0
        else:
            try:
                accel_dist = flag_accel_result[str(feed)+str(accel)][0]
                accel_time = flag_accel_result[str(feed)+str(accel)][1]
                decel_dist = flag_decel_result[str(feed)+str(decel)][0]
                decel_time = flag_decel_result[str(feed)+str(decel)][1]
            except:
                flag_accel_result[str(feed)+str(accel)] = accel_length(0, feed, accel)
                flag_decel_result[str(feed)+str(decel)] = accel_length(feed, 0, decel)

                accel_dist = flag_accel_result[str(feed) + str(accel)][0]
                accel_time = flag_accel_result[str(feed) + str(accel)][1]
                decel_dist = flag_decel_result[str(feed) + str(decel)][0]
                decel_time = flag_decel_result[str(feed) + str(decel)][1]

            steady_state_dist = abs(sum_dist_list[i]) - accel_dist - decel_dist


        if steady_state_dist <= 0:
            steady_state_dist = 0
            accel_dist = abs(sum_dist_list[i]) * 0.5
            decel_dist = accel_dist
            key = str(accel_dist)
            try:
                accel_time = flag_short_move[key][0]
                decel_time = flag_short_move[key][1]
            except:
                flag_short_move_list = []
                accel_time = findt(0, accel, accel_dist)
                v_current = findv(0, accel, accel_dist)
                decel_time = findt_using_v(v_current, 0, decel)
                flag_short_move_list.append(accel_time)
                flag_short_move_list.append(decel_time)
                flag_short_move[key] = flag_short_move_list


        steady_state_time = steady_state_dist/feed
        accel_dist_dict[i] = [accel_dist, steady_state_dist, decel_dist]
        accel_time_dict[i] = [accel_time,steady_state_time, decel_time]

        key = i #decel_abs_dist

        accel_abs_dist = decel_abs_dist + accel_dist
        steady_abs_dist = accel_abs_dist + steady_state_dist
        decel_abs_dist = steady_abs_dist + decel_dist

        accel_dist_abs_dict[key] = [accel_abs_dist, steady_abs_dist, decel_abs_dist]

        accel_abs_time = decel_abs_time + accel_time
        steady_abs_time = accel_abs_time + steady_state_time
        decel_abs_time = steady_abs_time + decel_time

        accel_time_abs_dict[key] = [accel_abs_time, steady_abs_time, decel_abs_time]


    # print("accel_dist_dict = ", accel_dist_dict)
    # print("accel_time_dict = ", accel_time_dict) # never used
    # print("accel_dist_abs_dict = ", accel_dist_abs_dict) # used in time-based function
    # print("accel_time_abs_dict = ", accel_time_abs_dict) # used in time-based function
    return accel_dist_abs_dict, accel_time_abs_dict
accel_profile_output = accel_profile(sum_dist_list)
accel_profile_distance = accel_profile_output[0]
accel_profile_time = accel_profile_output[1]
accel_profile_end = time.time()
print("length of accel_profile = ", accel_profile_end-accel_profile_start)

## creates dictionary of time and commands
calc_time_start = time.time()
def distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_dict):
    def findt(v_0, accel, x):
        import time
        from sympy import symbols, solve
        # v_0 = starting velocity
        # accel = acceleration/ramprate
        # x = distance traveled
        t = symbols('t')
        start = time.time()
        find_t = v_0 * t + 0.5 * (accel) * t ** 2 - x  # finds time
        sol_t = solve(find_t)
        for i in range(len(sol_t)):
            try:
                sol_t[i] >= 0
                t = sol_t[i]
            except TypeError:
                check = 0
        length_time = time.time() - start
        # print(length_time)
        return t

    time_list = []
    time_dict = {}
    x_current = 0
    t = 0
    distance = 0
    index_start = 0
    flag_rel_dist_accel = {}
    flag_rel_dist_max_vel = {}
    flag_rel_dist_decel = {}
    flag_count =0
    count = 0
    for j in range(len(distance_dict)):
        if type(distance_dict[j]) == str:
            time_dict[j] = distance_dict[j]
        else:
            distance += abs(distance_dict[j])
            for i in range(index_start, len(accel_profile_distance)):
                accel_region = accel_profile_distance[i][0]
                max_velocity_region = accel_profile_distance[i][1]
                decel_region = accel_profile_distance[i][2]

                if distance >= decel_region:
                    t_current = accel_profile_time[i][2]
                    x_current = decel_region
                    t = t_current
                    index_start += 1

                elif distance >= max_velocity_region:
                    t_current = accel_profile_time[i][1]
                    x_current = max_velocity_region
                    t = t_current

                elif distance >= accel_region:
                    t_current = accel_profile_time[i][0]
                    x_current = accel_region
                    t = t_current

                if distance < accel_region:
                    relative_distance = distance - x_current
                    try:
                        relative_distance = round(relative_distance, 7)
                        t_current = flag_rel_dist_accel[relative_distance]
                    except:
                        t_current = findt(0, accel, relative_distance)
                        relative_distance = round(relative_distance, 7)

                    t += t_current
                    flag_rel_dist_accel[relative_distance] = t_current
                    break

                elif distance < max_velocity_region:
                    count +=1
                    relative_distance = distance - x_current
                    try:
                        relative_distance = round(relative_distance,7)
                        t_current = flag_rel_dist_max_vel[relative_distance]
                        flag_count += 1
                    except:
                        t_current = relative_distance / feed  # findt(feed, 0, relative_distance)
                        relative_distance = round(relative_distance,7)
                    t += t_current
                    flag_rel_dist_max_vel[relative_distance] = t_current
                    break

                elif distance < decel_region:
                    relative_distance = distance - x_current

                    try:
                        relative_distance = round(relative_distance, 7)
                        t_current = flag_rel_dist_decel[relative_distance]
                    except:
                        t_current = findt(feed, decel, relative_distance)
                        relative_distance = round(relative_distance, 7)

                    t += t_current
                    flag_rel_dist_decel[relative_distance] = t_current
                    break

                if distance == decel_region or distance == max_velocity_region or distance == accel_region:
                    break

            time_output = t
            time_list.append(time_output)
            time_dict[j] = time_output
    print("max_vel_count = ", count)
    print("flag count = ", flag_count)
    return time_dict


time_dict = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_commands_dict )
start_delay_time = float(distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel,[start_delay])[0])
offset_time = float(distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, [abs(offset)])[0])

if offset < 0:
    offset_time = -offset_time

#offset_time = offset/feed

calc_time_end = time.time()
print("start_delay_time = ", start_delay_time, "\noffset_time = ", offset_time)
print("length of distance2time = ", calc_time_end-calc_time_start)

final_dict_start = time.time()
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
final_dict_end = time.time()
print("length of final_dicts = ", final_dict_end - final_dict_start)

end_time = time.time()
total_time = end_time - start_time
print("\nTime to translate distance to time: ", total_time)

print("time_based_dict_final = ", time_based_dict_final)
# print("set_press: ", set_press)
# print("initial_toggle: ", initial_toggle)
# print("command_dict_final = ", command_dict_final)

# ###### WAITING FOR PING ##################################
# print("\nWaiting for ping to start....")
# if __name__ == '__main__':
#
#     ser = openport(port_aerotech)
#     ser.reset_input_buffer()
#
#     told = time.time()
#     intervals = []
#
#     count = 0
#     while True:
#         bytesToRead = ser.inWaiting()
#         if bytesToRead > 0:
#             print('\r\n------------------')
#             message = ser.read(bytesToRead)  # creates type bytes, e.g., b'M792 ;SEND message\n'
#             message = message.decode(encoding='utf-8')  # creates type string, e.g., 'M792 ;SEND message\n'
#             print('Received command: ' + message)
#             if message == "start1\r\n":
#                 pause = 0.011305268287658692 #from AEROTECH_PING_data.txt
#
#                 exec(set_press)
#                 print("Setting the pressures....")
#
#                 break
#
# #### Executes Absolute timing ####
# print("Executing time-based code....")
# time.sleep(3-pause-start_delay_time)
#
# i = 0
# exec(initial_toggle)
# start_time = time.time()
# time_dict_list = []
# error_list = []
# real_time_list = []
# while (i < len(command_dict_final)):
#     current_time_stamp = time_based_dict_final[i] - offset_time
#     real_time = time.time() - start_time
#     # if i > 0:
#     #    current_time_stamp = current_time_stamp - offset/feed
#     if (real_time >= (current_time_stamp) and i == i):
#         exec(command_dict_final[i])
#         error = float(real_time - current_time_stamp)
#         print("Time: ", real_time)
#         print("\tCommands: ", command_dict_final[i])
#         print("\tError: ",(error))
#
#         if time_based_dict_final[i] != 0:
#             time_dict_list.append(current_time_stamp)
#             real_time_list.append(real_time)
#             error_list.append(error)
#
#         i += 1
# print("DONE!")
#
# serialPort1.close()
# serialPort2.close()
#
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
#



# for i in range(len(command_dict_final)):
#     print("if time = ", time_based_dict_final[i])
#     print("\t\texecute: ", command_dict_final[i])

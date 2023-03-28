
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

feed = 25
# feedrate mm/s
accel = 1000#1000 #700 # mm/s^2
decel = -1000#-1000 #-700 # mm/s^2

offset = 0#-1 #-1#-1.5#-2 # use a negative number to increase length of time/material being on
start_delay = 0#0.21389#0.405#0.21389 #0.27389 #0.29389 #0.25389 #0.21389 #0.3 #0.27 #0.3 # seconds
gcode_txt = "1Output_Gcode_checker_M1.txt"#"Y_move_accel_test_gcode.txt"#"1Output_Gcode_checker_M1.txt"#"1Output_Gcode_checker_both.txt" #"1Output_Gcode_checker_CoreShell.txt" #"1Output_Gcode_checker_both.txt" #"1Output_Gcode_checker_M1.txt"
number_of_ports_used = 1 #aka number of materials used

Z_var = "D"
z_height = 1.2
z_o= -150 + z_height

yes = 0
no = 1
home = no #do you want to home it?


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
# print("Pressure Box Ports: COM", press_com1, " and COM", press_com2)
# print("Python-Hyrel Port: COM", port_python)


# Declare empty lists.
print("Translating Gcode to Time....")
gcode_list = []
number_list = []
sum_list = []


#open and read in gcode txt file into a list - remove comments, spaces, random characters
with open(gcode_txt, "r") as gcode:
    for myline in gcode:  # For each elem in the file,
        gcode_list.append(myline.strip('\n'))
    gcode_list = [x for x in gcode_list if x != ""] # removes spaces
    #gcode_list = [x for x in gcode_list if ";" not in x] # removes comments
    gcode_list = [x for x in gcode_list if ";-" not in x]  # removes comments
    print('Original: ', gcode_list)
    gcode.close()

## find specific characters in a string
def find(s, ch): # s = string to search, ch = character to find
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
    angle = np.atan2(dy,dx)
    if angle < 0:
        angle = (np.pi*2)+angle
    return angle

## acceleration: find distance/time it takes to get to steady state velocity
def accel_length(v_0, v_f, accel):
    import sympy
    from sympy import symbols, solve
    # v_0 = starting velocity
    # max_v = desired feedrate #mm/s
    # accel = acceleration/ramprate
    x = symbols('x')
    t = symbols('t')
    v = symbols('v')
    find_x = v_0**2 + 2*accel*x-v_f**2 # finds distance to steady state velocity
    sol_x = solve(find_x)
    for i in range(len(sol_x)):
        try:
            sol_x[i] >= 0
            check = 1
        except TypeError:
            check = 0
        if check == 1:
            x_steady = sol_x[i]

    find_t = v_0 + accel*t - v_f # finds time to steady state velocity
    sol_t = solve(find_t)
    t_steady = sol_t[0]

    #print("distance to steady state: ", float(x_steady))
    return x_steady, t_steady

## acceleration: find distance/time for non zero acceleration
def findt(v_0, accel, x):
    from sympy import symbols, solve
    # v_0 = starting velocity
    # accel = acceleration/ramprate
    # x = distance traveled
    t = symbols('t')

    find_t = v_0 * t + 0.5 * (accel) * t ** 2 - x # finds time
    sol_t = solve(find_t)
    for i in range(len(sol_t)):
        try:
            sol_t[i] >= 0
            t = sol_t[i]
        except TypeError:
            check = 0
    return t

def findv(v_0, accel, x):
    from sympy import symbols, solve
    # v_0 = starting velocity
    # accel = acceleration/ramprate
    # x = distance traveled
    v = symbols('v')
    find_v = v_0 ** 2 + 2 * accel * x - v ** 2
    sol_v = solve(find_v)
    for i in range(len(sol_v)):
        try:
            sol_v[i] >= 0
            check = 1
        except TypeError:
            check = 0
        if check == 1:
            v = sol_v[i]
    return v

def findv_t(v_0, accel, t):
    from sympy import symbols, solve
    # v_0 = starting velocity
    # accel = acceleration/ramprate
    # t = time
    v = symbols('v')
    find_v = v_0 + accel*t - v
    sol_v = solve(find_v)
    v = sol_v
    return (float(v))

###create a gcode,  distance, and direction dictionary
X_index = {}
Y_index = {}
Z_index = {}
distance_dict = {}
command_dict = {}
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
            distance_dict[i] = pythag(x, y)
            direction_dict[i] = "Y/X"+ str(float(y)/float(x))
            distance_list.append(distance_dict[i])
            direction_list.append(direction_dict[i])

        if X_index[i] != [] and Y_index[i] == []:
            distance = gcode_dict[i][1].strip("X").strip("Y")
            distance_dict[i] = float(distance)
            direction_dict[i] = "X"
            distance_list.append(distance_dict[i])
            direction_list.append(direction_dict[i])


        if X_index[i] == [] and Y_index[i] != []:
            distance = gcode_dict[i][1].strip("X").strip("Y")
            distance_dict[i] = float(distance)
            direction_dict[i] = "Y"
            distance_list.append(distance_dict[i])
            direction_list.append(direction_dict[i])

        if X_index[i] == [] and Y_index[i] == [] and Z_index[i] != []:
            distance = gcode_dict[i][1].strip("X").strip("Y").strip("Z")
            distance_dict[i] = float(distance)
            direction_dict[i] = "Z"
            distance_list.append(distance_dict[i])
            direction_list.append(direction_dict[i])

    else:
        command = gcode_dict[i][0]
        distance_dict[i] = gcode_dict[i][0]
        command_dict[i] = gcode_dict[i][0]

        #distance_list.append(distance_dict[i])

    if 'G3' in gcode_dict[i]:
        x = gcode_dict[i][1].strip("X")
        y = gcode_dict[i][2].strip("Y")
        I = gcode_dict[i][3].strip("I")
        J = gcode_dict[i][4].strip("J")
        R = pythag(I, J)

# print("X_index = ", X_index)
# print("Y_index = ", Y_index)

# print("gcode_dict = ", gcode_dict)
print("distance_dict = ", distance_dict)
# print("command_dict = ", command_dict)
# print("direction_dict = ", direction_dict)
# print("g_command_dict = ", g_command_dict)
# print("distance_list = ", distance_list)
# print("direction_list = ", direction_list)
# print("g_command_list = ", g_command_list)

## creates total distance list (doesn't take direction into account)
total_dist_dict = {}
total_dist = 0
for i in range(len(distance_dict)):
    if type(distance_dict[i])==float:
        distance_dict[i] = abs(distance_dict[i])
        total_dist = total_dist + distance_dict[i]
        total_dist_dict[i] = total_dist
    else:
        total_dist_dict[i] = distance_dict[i]

print("total_dist_dict = ", total_dist_dict)


## creates simplified gcode for 3d printer and for use in acceleration profile
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


print("sum_dist_list = ", sum_dist_list)
print("sum_dir_list = ", sum_dir_list)
print("sum_g_list = ", sum_g_list)
print("sum_gcode_list = ", sum_gcode_list)
# print("group_dist_accel_dict = ", group_dist_accel_dict)
# print("group_abs_dist_accel_dict = ", group_abs_dist_accel_dict)


## create txt for gcode used in 3d printer
with open("2Output_Final_gcode.txt", "w") as f:
    f.write("DVAR $hFile\n\r")
    f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP RATE ' +str(accel)+ '\n\r')

    f.write("ENABLE X Y " + Z_var + "\n")
    if home == yes:
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
    f.write('\nG4 P2\nFILEWRITE $hFile, "start2"\nG4 P3\n\r')

    for i in range(len(sum_gcode_list)):
        coord = sum_gcode_list[i]
        G_command = sum_g_list[i]
        f.write( G_command + " " + coord + "\r\n")
    f.write('\n\rFILECLOSE $hFile\nM02')

## creates acceleration profile
accel_dist_dict = {}


accel_time_dict = {}
accel_time_total_dict = {}


accel_dist_abs_dict = {}
accel_dist_abs_range_dict = {}

accel_time_abs_dict = {}
accel_time_abs_range_dict = {}
accel_time_abs_total_dict = {}

third = 0
third_t = 0

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
        max_vel = findv(0, accel, accel_dist)
        decel_time = findt(max_vel, decel, decel_dist)

    steady_state_time = steady_state_dist/feed
    accel_dist_dict[i] = [accel_dist, steady_state_dist, decel_dist]
    accel_time_dict[i] = [accel_time,steady_state_time, decel_time]
    accel_time_total_dict[i] = accel_time+steady_state_time+decel_time

    prev_third = third
    first = prev_third + accel_dist
    second = first + steady_state_dist
    third = second + decel_dist

    accel_dist_abs_dict[i] = [first, second, third]
    accel_dist_abs_range_dict[i] = [[prev_third,first], [first,second],[second,third]]

    prev_third_t = third_t
    first_t = prev_third_t + accel_time
    second_t = first_t + steady_state_time
    third_t = second_t + decel_time

    accel_time_abs_dict[i] = [first_t, second_t, third_t]
    accel_time_abs_range_dict[i] = [[prev_third_t, first_t], [first_t, second_t], [second_t, third_t]]
    accel_time_abs_total_dict[i] = third_t

    max_time = third_t

print("accel_dist_dict = ", accel_dist_dict)
print("accel_time_dict = ", accel_time_dict)
print("accel_dist_abs_dict = ", accel_dist_abs_dict)
# print("accel_dist_abs_range_dict = ", accel_dist_abs_range_dict)
print("accel_time_abs_dict = ", accel_time_abs_dict)
# print("accel_time_abs_range_dict = ", accel_time_abs_range_dict)
# print("accel_time_total_dict = ", accel_time_total_dict)
# print("accel_time_abs_total_dict = ", accel_time_abs_total_dict)

# ## groups commands and distance into a dictionary based on accel profile
# group_dist_accel_dict = {}
# start = 1
# count = 0
# group_abs_dist_accel_dict = {}
# total_sum = 0
# for j in range(len(sum_dist_list)):
#     dist = []
#     group_sum_dist = []
#     sum_dist = abs(distance_list[count])
#     for i in range(start, len(distance_list)):
#         if sum_dist <= abs(sum_dist_list[j]):
#             total_sum += abs(distance_list[i-1]) # this is for creating list of absolute distances
#             group_sum_dist.append(total_sum) # this is for creating list of absolute distances
#
#             sum_dist += abs(distance_list[i]) # this is for creating list of relative distances
#             dist.append(abs(distance_list[i-1]))  # this is for creating list of relative distances
#             count = count + 1
#         else:
#             count = count
#         start = count + 1
#     group_dist_accel_dict[j] = dist
#     group_abs_dist_accel_dict[j] = group_sum_dist
#
# print("group_dist_accel_dict = ", group_dist_accel_dict)
# print("group_abs_dist_accel_dict = ", group_abs_dist_accel_dict)


## groups commands and distance into a dictionary based on order of occurance
# grouped = []
# count = 0
# grouped_all_dict = {}
#
# for i in range(len(distance_dict)):
#     if type(distance_dict[i])==float:
#         distance_dict[i] = abs(distance_dict[i])
#     if i == 0:
#         grouped.append(distance_dict[i])
#     elif type(distance_dict[i]) == type(distance_dict[i-1]):
#         grouped.append(distance_dict[i])
#     else:
#         grouped_all_dict[count] = grouped
#         grouped = []
#         grouped.append(distance_dict[i])
#         count = count + 1
#
# print("grouped_all_dict = ", grouped_all_dict)
#
# count =  0
# count_d = 0
# grouped_1_dict = {}
# grouped_2_dict = {}
# for i in range(len(grouped_all_dict)):
#     if i%2 == 0:
#         grouped_1_dict[count]  = grouped_all_dict[i]
#         count += 1
#     else:
#         grouped_2_dict[count_d] = grouped_all_dict[i]
#         count_d += 1
#
# if type(grouped_1_dict[0][0]) != float:
#     grouped_command_dict = grouped_1_dict
#     grouped_dist_dict = grouped_2_dict
# else:
#     grouped_command_dict = grouped_2_dict
#     grouped_dist_dict = grouped_1_dict
#
# print("grouped_command_dict = ", grouped_command_dict)
# print("grouped_dist_dict = ", grouped_dist_dict)


# ## groups commands and ABSOLUTE distance into a dictionary based on order of occurance
# grouped = []
# count = 0
# grouped_all_abs_dict = {}
#
# for i in range(len(total_dist_dict)):
#     if type(total_dist_dict[i])==float:
#         total_dist_dict[i] = abs(total_dist_dict[i])
#     if i == 0:
#         grouped.append(total_dist_dict[i])
#     elif type(total_dist_dict[i]) == type(total_dist_dict[i - 1]):
#         grouped.append(total_dist_dict[i])
#     else:
#         grouped_all_abs_dict[count] = grouped
#         grouped = []
#         grouped.append(total_dist_dict[i])
#         count = count + 1
#
# print("grouped_all_abs_dict = ", grouped_all_dict)
#
# count =  0
# count_d = 0
# grouped_1_abs_dict = {}
# grouped_2_abs_dict = {}
# for i in range(len(grouped_all_abs_dict)):
#     if i%2 == 0:
#         grouped_1_abs_dict[count]  = grouped_all_abs_dict[i]
#         count = count + 1
#     else:
#         grouped_2_abs_dict[count_d] = grouped_all_abs_dict[i]
#         count_d = count_d + 1
#
# if type(grouped_1_abs_dict[0][0]) != float:
#     grouped_command_abs_dict = grouped_1_abs_dict
#     grouped_dist_abs_dict = grouped_2_abs_dict
# else:
#     grouped_command_abs_dict = grouped_2_abs_dict
#     grouped_dist_abs_dict = grouped_1_abs_dict
#
# print("grouped_command_abs_dict = ", grouped_command_abs_dict)
# print("grouped_dist_abs_dict = ", grouped_dist_abs_dict)



v_current = 0
time_dict = {}
final_time_based_list = []
accel_region = 0
steady_region = 0
decel_region = 0
t = 0
t_accel_remaining = 0
t_steady_remaining = 0
t_decel_remaining = 0
t_accel_total = 0
t_steady_total = 0
t_decel_total = 0




for i in range(len(group_dist_accel_dict)):
    # print("----NEW ACCEL PROFILE----")
    t += t_accel_remaining + t_steady_remaining + t_decel_remaining
    # print(t_accel_remaining, t_steady_remaining, t_decel_remaining)
    # print('time leftover from previous moves = ', t)
    accel_region = accel_dist_dict[i][0]
    steady_region = accel_dist_dict[i][1]
    decel_region = accel_dist_dict[i][2]

    accel_time = accel_time_dict[i][0]
    steady_time = accel_time_dict[i][1]
    decel_time = accel_time_dict[i][2]

    time_list = []
    t_accel_remaining = accel_time
    t_steady_remaining = steady_time
    t_decel_remaining = decel_time
    for distance in group_dist_accel_dict[i]:
        distance = abs(distance)
        #distance = group_dist_accel_dict[i][j]
        # print("-------distance = ", distance)
        if accel == 0:
            t_accel_remaining = 0
            t_steady_remaining = 0
            t_decel_remaining = 0
            t += distance/feed

        else:
            if accel_region > 0:
                # print('START distance accelerating = ', accel_region)
                if distance < accel_region:
                    # print("distance accelerating = ", distance)
                    t_accel = findt(v_current, accel, distance)
                    t_accel_remaining -= t_accel
                    # print("time accelerating = ", t_accel)
                    t += t_accel
                    # print("running total time = ", t)
                    v_current = findv(v_current, accel, distance)
                    accel_region -= distance
                    distance = 0
                    # print("time accelerating = ", t_accel)
                    # print("distance left to accelerate = ", accel_region)
                    # print("time left to accelerate = ", t_accel_remaining)

                else:
                    # print("distance accelerating = ", distance)
                    t_accel = findt(v_current, accel, accel_region)
                    t_accel_remaining -= t_accel
                    # print("time accelerating = ", t_accel)
                    t += t_accel
                    # print("running total time = ", t)
                    v_current = feed #findv(v_current, accel, accel_region)
                    distance -= accel_region
                    accel_region = 0
                    # print("time accelerating = ", t_accel)
                    # print("distance left to accelerate = ", accel_region)
                    # print("distance left before next command = ", distance)
                    # print("time left to accelerate = ", t_accel_remaining)

            if steady_region > 0 and accel_region == 0:
                t_accel_remaining = 0
                # print('START amount of distance at max velocity = ', steady_region)
                if distance < steady_region:
                    t_steady = findt(v_current, 0, distance)
                    t_steady_remaining -= t_steady
                    t += t_steady
                    v_current = feed #findv(v_current, 0, distance)
                    steady_region -= distance
                    distance = 0
                    # print("max velocity t = ", t_steady)
                    # print("END distance left at max velocity = ", steady_region)
                else:
                    t_steady = findt(v_current, 0, steady_region)
                    t_steady_remaining -= t_steady
                    t += t_steady
                    v_current = feed #findv(v_current, 0, steady_region)
                    distance -= steady_region
                    steady_region = 0
                    # print("max velocity t = ", t_steady)
                    # print("distance left at max velocity = ", steady_region)
                    # print("END distance left before next command = ", distance)
            if decel_region >= 0 and steady_region == 0 and accel_region == 0:
                t_accel_remaining = 0
                t_steady_remaining = 0
                if distance < decel_region:
                    t_decel = findt(v_current, decel, distance)
                    t_decel_remaining -= t_decel
                    t += t_decel
                    v_current = findv(v_current, decel, distance)
                    decel_region -= distance
                    distance = 0
                    # print("decelerating t = ", t_decel)
                    # print("distance left to decel = ", decel_region)
                else:
                    t_decel = findt(v_current, decel, decel_region)
                    t_decel_remaining -= t_decel
                    t += t_decel
                    v_current = 0 #findv(v_current, decel, decel_region)
                    distance -= decel_region
                    decel_region = 0
                    # print("decelerating t = ", t_decel)
                    # print("distance left to decel = ", decel_region)
                    # print("distance left before next command = ", distance)
        time_list.append(t)
        final_time_based_list.append(t)
        #t = 0 # t = 0 if you want relative time-stamps; if you want absolute, comment out
    time_dict[i] = time_list


# print(time_dict)
print(final_time_based_list)

command_list = []
time_based = []
time_based_dict_final = {}
time_based_dict_unsummed = {}
command_dict_final = {}

count_t = 0
dict_count_t = 0
sum_time_based = 0
dict_count_c = 0
start_count_c = 0
initial_commands = []
initial_commands_trigger = 0

for i in range(len(distance_dict)):
    entry = distance_dict[i]
    dict_count_c = dict_count_t
    if type(entry) == float:
        # sum_time_based += final_time_based_list[count_t] #if times are relative
        time_based.append(final_time_based_list[count_t])
        time_based_dict_final[dict_count_t] = final_time_based_list[count_t]
        time_based_dict_unsummed[dict_count_t] = time_based
        command_list = []
        count_t += 1
        start_count_c = 0
        initial_commands_trigger = 1
    else:
        time_based = []
        # sum_time_based = 0 # if times are relative
        command_list.append(entry)
        if initial_commands_trigger == 0:
            initial_commands = command_list
        else:
            command_dict_final[dict_count_c] = command_list#'[%s]' % ', '.join(map(str, command_list[:]))
            if start_count_c == 0:
                dict_count_t += 1
                # dict_count_t += 1
                start_count_c = 1

    set_press = '[%s]' % ', '.join(map(str,initial_commands[:number_of_ports_used]))
    initial_toggle ='[%s]' % ', '.join(map(str, initial_commands[number_of_ports_used:]))

for i in range(len(command_dict_final)):
    command_list = command_dict_final[i]
    command_dict_final[i] = '[%s]' % ', '.join(map(str, command_list))

print("time_based_dict_unsummed = ", time_based_dict_unsummed)
print("time_based_dict_final = ", time_based_dict_final)
print("command_dict_final = ", command_dict_final)
print("initial_commands = ",initial_commands )

# set_press = initial_commands[:number_of_ports_used]
# initial_toggle = initial_commands[number_of_ports_used:]
print("set_press =", set_press)
print("initial_toggle = ", initial_toggle)

print("type in time_based_dict_final = ", type(time_based_dict_final[5]))

###### WAITING FOR PING ##################################
print("Waiting for ping to start....")
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
                tstart1 = time.time()

            if message == "start2\r\n":
                tstart2 = time.time()
                delta = tstart2 - tstart1
                pause = 2 - delta

                exec(set_press)
                print("Setting the pressures....")

                break

# # ## Executes Absolute timing!!!!!!! NOTE: It starts after the
print("Executing time-based code....")

if pause >= 0:
    time.sleep(3 + 2*pause - start_delay)
else:
    time.sleep(3 + pause - start_delay)


i = 0
exec(initial_toggle)
start_time = time.time()
error_list = []
while (i < len(command_dict_final)):
    current_time_stamp = time_based_dict_final[i] - offset
    real_time = time.time() - start_time
    # if i > 0:
    #    current_time_stamp = current_time_stamp - offset/feed
    if (real_time >= (current_time_stamp) and i == i):
        exec(command_dict_final[i])
        error = real_time - current_time_stamp
        print("Time: ", real_time)
        print("\tCommands: ", command_dict_final[i])
        print("\tError: ",(error))
        error_list.append(error)
        i += 1
print("DONE!")

serialPort1.close()
serialPort2.close()

avg_error = np.average(error_list)
std_error = np.std(error_list)

print("avg_error = ", avg_error)
print("std_error = ", std_error)

with open("Time_error.txt", "a") as f:
    from datetime import datetime
    now = datetime.now() # datetime object containing current date and time
    dt_string = now.strftime("%d/%m/%Y %H:%M:%S")     # dd/mm/YY H:M:S
    f.write('\n2Streamlined_aerotech')
    f.write('\rdate and time: ' + dt_string)
    f.write("\rerror_list = " + str(error_list))
    f.write("\ravg_error = " + str(avg_error))
    f.write("\rstd_error = " + str(std_error))
# i = 0
# exec(initial_toggle)
# start_time = time.time()
# while (i < len(command_dict_final)):
#     current_time_stamp = time_based_dict_final[i]
#     if i > 0:
#        current_time_stamp = current_time_stamp - offset/feed
#     if (time.time() - start_time >= (current_time_stamp) and i == i):
#         print("Time: ", (time.time()-start_time))
#         print("Commands: ", command_dict_final[i])
#         exec(command_dict_final[i])
#         i += 1
# print("DONE!")
#
# serialPort1.close()
# serialPort2.close()


# for i in range(len(command_dict_final)):
#     print("if time = ", time_based_dict_final[i])
#     print("\t\texecute: ", command_dict_final[i])

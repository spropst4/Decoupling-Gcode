############################## INPUTS ####################################
import math
import numpy as np
from math import sqrt
import time

from datetime import datetime
from datetime import date
now = datetime.now() # datetime object containing current date and time
current_date = date.today()
dt_string = now.strftime("%d/%m/%Y %H:%M:%S")     # dd/mm/YY H:M:S
############################ INPUTS #############################################
feed = 25 # feedrate mm/s
accel = 1000#700 # mm/s^2
decel = -1000#-700 # mm/s^2

offset = 0 #use a negative number to increase length of time/material being on (units in mm)
start_delay =0 #(units in mm)
defining = "y1"
testing = "y = 1, feed = " +str(feed) + " mm/s, accel = " + str(accel) + " mm/s^2"
gcode_txt_imported = "1DGC_Generate_Checkerboard_M1.txt"
#"Y_move_test_continuous_gcode.txt" #"Y_move_test_no_x_gcode.txt"
#"1Output_Gcode_checker_M1.txt"  #"1Output_Gcode_checker_CoreShell.txt" #"1Output_Gcode_checker_both.txt"
final_gcode_txt_export = "1DGC_Generate_Checkerboard_M1_aerotech.txt"
# "Y_move_test_continuous_aerotech_" +str(defining) + "_f"+str(feed)+'_a'+str(accel) +'_' + str(current_date) +'.txt'
# "VOID.txt"
# "Y_move_test_continuous_aerotech.txt"

number_of_ports_used = 1 # (aka number of materials used)

Z_var = "D"
z_height = 0.2
z_o= -150 + z_height

home = False  #do you want to home it? (True = yes)

# Open the port for the python-hyrel connection
port_aerotech = 1 #port named in python code to connect to aerotech
port_python = 2 #this port is named in aerotech code to connect to python

#########################################################################
print("Feedrate = ", feed, "mm/s")
print("Acceleration = ", accel, "mm/s^2", "\nDeceleration = ", decel, "mm/s^2")
print("\r\nImporting Gcode....")

start_time = time.time()
print("\r\nImporting Gcode....")

## open and read in gcode txt file into a list - remove comments, spaces, random characters
def open_gcode(gcode_txt):
    gcode_list = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            gcode_list.append(myline.strip('\n'))
        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        #gcode_list = [x for x in gcode_list if ";" not in x] # removes comments
        gcode_list = [x for x in gcode_list if ";--" not in x]  # removes comments
        gcode_list = [x for x in gcode_list if "---" not in x]  # removes comments
        #print('Original: ', gcode_list)
        gcode.close()
        return gcode_list
gcode_list = open_gcode(gcode_txt_imported)
print(gcode_list)
print("Translating Gcode to Time....")

## splits up gcode into directions, distances, G command type (G1, G2, G3, etc)
## create a gcode,  distance, and direction dictionary
parse_start = time.time()
def parse_gcode(gcode_list):

    ## Finds G-command (i.e., G1, G2, G3)
    def find_G(gcode_dict, ch):  # s = string to search, ch = character to find
        for elem in enumerate(gcode_dict):
            if ch in elem[1]:
                return elem[1] # finds location of character, strips it, and outputs numerical number
        else:
            return None

    def find_distances(gcode_dict, ch):  # s = string to search, ch = character to find
        # ch = character to find
        output =None,None
        if "G" in gcode_dict[0]:
            for elem in enumerate(gcode_dict):
                if ch in elem[1]:
                    output = float(elem[1].strip(ch)), ch # finds location of character, strips it, and outputs numerical number
        return output


    ## pythag thm
    def pythag(x, y):
        return (sqrt(abs(float(x)) ** 2 + abs(float(y)) ** 2))

    ## find arc_angle
    def find_theta(X, Y, I, J): # finds angle between intersecting lines
        import math
        from math import atan2
        a = math.atan2(-J, -I)
        b = math.atan2(Y - J, X - I)
        theta = b - a
        return theta

    G_command_dict = {}
    gcode_dict = {}

    X_dist_dict = {}
    Y_dist_dict = {}
    Z_dist_dict = {}
    I_dist_dict = {}
    J_dist_dict = {}
    All_dist_dict = {}
    All_var_dict = {}
    for i in range(len(gcode_list)):
        gcode_dict[i] = gcode_list[i].split(" ")

        ## Stores type of G-command for each line
        G_command_dict[i] = find_G(gcode_dict[i], "G")

        ## Stores distance values for each command
        find_X = find_distances(gcode_dict[i], "X")
        find_Y = find_distances(gcode_dict[i], "Y")
        find_Z = find_distances(gcode_dict[i], "Z")
        find_I = find_distances(gcode_dict[i], "I")
        find_J = find_distances(gcode_dict[i], "J")

        X_dist_dict[i] = find_X[0]
        Y_dist_dict[i] = find_Y[0]
        Z_dist_dict[i] = find_Z[0]
        I_dist_dict[i] = find_I[0]
        J_dist_dict[i] = find_J[0]

        All_dist_dict[i] = [X_dist_dict[i], Y_dist_dict[i], Z_dist_dict[i], I_dist_dict[i], J_dist_dict[i]]
        All_var_dict[i] = [find_X[1], find_Y[1],find_Z[1], find_I[1], find_J[1]]

    print(gcode_dict)
    print(G_command_dict)
    print(X_dist_dict)
    print(Y_dist_dict)
    print(Z_dist_dict)
    print(I_dist_dict)
    print(J_dist_dict)
    print(All_dist_dict)
    print(All_var_dict)

    return gcode_dict, G_command_dict, X_dist_dict, Y_dist_dict, Z_dist_dict, I_dist_dict, J_dist_dict, All_dist_dict, All_var_dict

parse_output = parse_gcode(gcode_list)
gcode_dict = parse_output[0]
G_command_dict = parse_output[1]
X_dist_dict = parse_output[2]
Y_dist_dict = parse_output[3]
Z_dist_dict = parse_output[4]
I_dist_dict = parse_output[5]
J_dist_dict = parse_output[6]
All_dist_dict = parse_output[7]
All_var_dict = parse_output[8]

condense_start = time.time()
## creates simplified gcode for 3d printer and for use in acceleration profile
def condense_gcode(gcode_dict, G_command_dict, All_var_dict, All_dist_dict):
    grouped = 0
    ungrouped = 0
    dict_count = 0
    start_point = 0
    end_point = 0
    grouped_dict = {}
    # for i in range(1, len(gcode_dict)):
    #     current_G_command = G_command_dict[i]
    #
    #     if G_command_dict[i] == G_command_dict[i-1] and All_var_dict[i]== All_var_dict[i-1]:
    #         ungrouped = 0
    #         grouped += 1
    #         start_point = i - grouped
    #         end_point = i
    #
    #     else:
    #         grouped = 0
    #         if i > 1 and grouped == 0 and ungrouped == 0:
    #             grouped_dict[dict_count] = [start_point, end_point]
    #             dict_count += 1
    #         ungrouped += 1

    sum_dist = All_dist_dict[0]
    for i in range(1, len(gcode_dict)):
        current_G_command = G_command_dict[i]
        if G_command_dict[i] == G_command_dict[i - 1] and All_var_dict[i] == All_var_dict[i - 1]:
            if G_command_dict[i] == "G1":
                for j in range(len(All_dist_dict[i])):
                    if All_dist_dict[i][j] != None:
                        sum_dist[j] += All_dist_dict[i][j]
                print(sum_dist)


        else:
            sum_dist = All_dist_dict[i]











condense_gcode(gcode_dict, G_command_dict, All_var_dict, All_dist_dict)
# def generate_gcode(final_gcode_txt_export, accel, Z_var, z_o, feed,sum_gcode_list, sum_g_list):
#     ## create txt for gcode used in 3d printer
#     with open(final_gcode_txt_export, "w", 0) as f:
#         f.write("DVAR $hFile\n\r")
#         f.write('G71 \nG76 \nG91	;G90 = absolute, G91 = relative \nG68 \nRAMP TYPE LINEAR X Y \nRAMP RATE ' +str(accel)+ '\n\rVELOCITY OFF\n\r')
#
#         f.write("ENABLE X Y " + Z_var + "\n")
#         if home == True:
#             f.write("HOME X Y " + Z_var + "\r\n")
#             f.write("'G90\n'G0 X0 Y0 " + Z_var + "0\n'G91\n\r")
#         else:
#             f.write("'HOME X Y " + Z_var + "\r\n")
#             f.write("G90\nG0 X0 Y0 " + Z_var + "0\nG91\n\r")
#
#         f.write(";Begin Motion\n")
#         f.write("G0 X150 Y50 \n")
#         f.write("G0 " + Z_var + str(z_o) + "\n")
#         f.write("G1 F" + str(feed) + "\n\r")
#
#         f.write("\n\rFILECLOSE")
#         f.write('\n$hFile = FILEOPEN "COM'+str(port_python) +'", 2')
#         f.write('\nCOMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"')
#         f.write('\nCOMMSETTIMEOUT $hFile, -1, -1, 1000')
#         f.write('\n\rFILEWRITE $hFile, "start1"')
#         f.write('\nG4 P3\n\r')
#
#         for i in range(len(sum_gcode_list)):
#             coord = sum_gcode_list[i]
#             G_command = sum_g_list[i]
#             f.write( G_command + " " + coord + "\r\n")
#         f.write('\n\rFILECLOSE $hFile\nM02')
#     print("\n\r", final_gcode_txt_export, " has been created\n\r")
#     return f
# create_gcode = generate_gcode(final_gcode_txt_export, accel, Z_var, z_o, feed,sum_gcode_list, sum_g_list)
# accel_profile_start = time.time()
# ## creates acceleration profile
# def accel_profile(sum_dist_list):
#     import time
#     def accel_length(v_0, v_f, accel):
#         from sympy import symbols, solve
#         # v_0 = starting velocity
#         # max_v = desired feedrate #mm/s
#         # accel = acceleration/ramprate
#         x = symbols('x')
#         t = symbols('t')
#         v = symbols('v')
#         find_x = v_0 ** 2 + 2 * accel * x - v_f ** 2  # finds distance to steady state velocity
#         sol_x = solve(find_x)
#         for i in range(len(sol_x)):
#             try:
#                 sol_x[i] >= 0
#                 x_steady = sol_x[i]
#                 #x_steady = round(x_steady, 10)
#             except TypeError:
#                 print("error in value of x; it may be imaginary")
#
#         find_t = v_0 + accel * t - v_f  # finds time to steady state velocity
#         sol_t = solve(find_t)
#         t_steady = sol_t[0]
#         #t_steady = round(t_steady, 10)
#         return x_steady, t_steady
#     def findt(v_0, accel, x):
#         from sympy import symbols, solve
#         # v_0 = starting velocity
#         # accel = acceleration/ramprate
#         # x = distance traveled
#         t = symbols('t')
#
#         find_t = v_0 * t + 0.5 * (accel) * t ** 2 - x  # finds time
#         sol_t = solve(find_t)
#         for i in range(len(sol_t)):
#             try:
#                 sol_t[i] >= 0
#                 t = sol_t[i]
#                 #t = round(t, 10)
#             except TypeError:
#                 print("error when calcuating time; might be getting an imaginary number.")
#         return t
#     def findv(v_0, accel, x):
#         from sympy import symbols, solve
#         # v_0 = starting velocity
#         # accel = acceleration/ramprate
#         # x = distance traveled
#         # v = symbols('v')
#         # find_v = v_0 ** 2 + 2 * accel * x - v ** 2
#         # sol_v = solve(find_v)
#         try:
#             v = sqrt(v_0**2 + 2*accel*x)
#             #v = round(v, 10)
#         except TypeError:
#             print("error when calcuating velocity; might be getting an imaginary number.")
#
#         return v
#         #return float(v)
#     def findt_using_v(v_0, v_f, accel):
#         t = (v_f - v_0)/accel
#         #t = round(t, 10)
#         return float(t)
#
#     accel_dist_dict = {}
#     accel_time_dict = {}
#     accel_dist_abs_dict = {}
#     accel_time_abs_dict = {}
#     flag_accel_result = {}
#     flag_decel_result = {}
#     flag_short_move = {}
#     decel_abs_dist = 0
#     decel_abs_time = 0
#
#     for i in range(len(sum_dist_list)):
#         if accel == 0:
#             steady_state_dist = abs(sum_dist_list[i])
#             accel_dist = 0
#             decel_dist = 0
#             accel_time = 0
#             decel_time = 0
#         else:
#             try:
#                 accel_dist = flag_accel_result[str(feed)+str(accel)][0]
#                 accel_time = flag_accel_result[str(feed)+str(accel)][1]
#                 decel_dist = flag_decel_result[str(feed)+str(decel)][0]
#                 decel_time = flag_decel_result[str(feed)+str(decel)][1]
#             except:
#                 flag_accel_result[str(feed)+str(accel)] = accel_length(0, feed, accel)
#                 flag_decel_result[str(feed)+str(decel)] = accel_length(feed, 0, decel)
#
#                 accel_dist = flag_accel_result[str(feed) + str(accel)][0]
#                 accel_time = flag_accel_result[str(feed) + str(accel)][1]
#                 decel_dist = flag_decel_result[str(feed) + str(decel)][0]
#                 decel_time = flag_decel_result[str(feed) + str(decel)][1]
#
#             steady_state_dist = abs(sum_dist_list[i]) - accel_dist - decel_dist
#
#
#         if steady_state_dist <= 0:
#             steady_state_dist = 0
#             accel_dist = abs(sum_dist_list[i]) * 0.5
#             decel_dist = accel_dist
#             key = str(accel_dist)
#             try:
#                 accel_time = flag_short_move[key][0]
#                 decel_time = flag_short_move[key][1]
#             except:
#                 flag_short_move_list = []
#                 accel_time = findt(0, accel, accel_dist)
#                 v_current = findv(0, accel, accel_dist)
#                 decel_time = findt_using_v(v_current, 0, decel)
#                 flag_short_move_list.append(accel_time)
#                 flag_short_move_list.append(decel_time)
#                 flag_short_move[key] = flag_short_move_list
#
#
#         steady_state_time = steady_state_dist/feed
#         accel_dist_dict[i] = [accel_dist, steady_state_dist, decel_dist]
#         accel_time_dict[i] = [accel_time,steady_state_time, decel_time]
#
#         key = i #decel_abs_dist
#
#         accel_abs_dist = decel_abs_dist + accel_dist
#         steady_abs_dist = accel_abs_dist + steady_state_dist
#         decel_abs_dist = steady_abs_dist + decel_dist
#
#         accel_dist_abs_dict[key] = [accel_abs_dist, steady_abs_dist, decel_abs_dist]
#
#         accel_abs_time = decel_abs_time + accel_time
#         steady_abs_time = accel_abs_time + steady_state_time
#         decel_abs_time = steady_abs_time + decel_time
#
#         accel_time_abs_dict[key] = [accel_abs_time, steady_abs_time, decel_abs_time]
#
#
#     # print("accel_dist_dict = ", accel_dist_dict)
#     # print("accel_time_dict = ", accel_time_dict) # never used
#     # print("accel_dist_abs_dict = ", accel_dist_abs_dict) # used in time-based function
#     # print("accel_time_abs_dict = ", accel_time_abs_dict) # used in time-based function
#     return accel_dist_abs_dict, accel_time_abs_dict
# accel_profile_output = accel_profile(sum_dist_list)
# accel_profile_distance = accel_profile_output[0]
# accel_profile_time = accel_profile_output[1]
# accel_profile_end = time.time()
# print("length of accel_profile = ", accel_profile_end-accel_profile_start)
#
# ## creates dictionary of time and commands
# calc_time_start = time.time()
# def distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_dict):
#     def findt(v_0, accel, x):
#         import time
#         from sympy import symbols, solve
#         # v_0 = starting velocity
#         # accel = acceleration/ramprate
#         # x = distance traveled
#         t = symbols('t')
#         start = time.time()
#         find_t = v_0 * t + 0.5 * (accel) * t ** 2 - x  # finds time
#         sol_t = solve(find_t)
#         for i in range(len(sol_t)):
#             try:
#                 sol_t[i] >= 0
#                 t = sol_t[i]
#             except TypeError:
#                 check = 0
#         length_time = time.time() - start
#         # print(length_time)
#         return t
#
#     time_list = []
#     time_dict = {}
#     x_current = 0
#     t = 0
#     distance = 0
#     index_start = 0
#     flag_rel_dist_accel = {}
#     flag_rel_dist_max_vel = {}
#     flag_rel_dist_decel = {}
#     flag_count =0
#     count = 0
#     for j in range(len(distance_dict)):
#         if type(distance_dict[j]) == str:
#             time_dict[j] = distance_dict[j]
#         else:
#             distance += abs(distance_dict[j])
#             for i in range(index_start, len(accel_profile_distance)):
#                 accel_region = accel_profile_distance[i][0]
#                 max_velocity_region = accel_profile_distance[i][1]
#                 decel_region = accel_profile_distance[i][2]
#
#                 if distance >= decel_region:
#                     t_current = accel_profile_time[i][2]
#                     x_current = decel_region
#                     t = t_current
#                     index_start += 1
#
#                 elif distance >= max_velocity_region:
#                     t_current = accel_profile_time[i][1]
#                     x_current = max_velocity_region
#                     t = t_current
#
#                 elif distance >= accel_region:
#                     t_current = accel_profile_time[i][0]
#                     x_current = accel_region
#                     t = t_current
#
#                 if distance < accel_region:
#                     relative_distance = distance - x_current
#                     try:
#                         relative_distance = round(relative_distance, 7)
#                         t_current = flag_rel_dist_accel[relative_distance]
#                     except:
#                         t_current = findt(0, accel, relative_distance)
#                         relative_distance = round(relative_distance, 7)
#
#                     t += t_current
#                     flag_rel_dist_accel[relative_distance] = t_current
#                     break
#
#                 elif distance < max_velocity_region:
#                     count +=1
#                     relative_distance = distance - x_current
#                     try:
#                         relative_distance = round(relative_distance,7)
#                         t_current = flag_rel_dist_max_vel[relative_distance]
#                         flag_count += 1
#                     except:
#                         t_current = relative_distance / feed  # findt(feed, 0, relative_distance)
#                         relative_distance = round(relative_distance,7)
#                     t += t_current
#                     flag_rel_dist_max_vel[relative_distance] = t_current
#                     break
#
#                 elif distance < decel_region:
#                     relative_distance = distance - x_current
#
#                     try:
#                         relative_distance = round(relative_distance, 7)
#                         t_current = flag_rel_dist_decel[relative_distance]
#                     except:
#                         t_current = findt(feed, decel, relative_distance)
#                         relative_distance = round(relative_distance, 7)
#
#                     t += t_current
#                     flag_rel_dist_decel[relative_distance] = t_current
#                     break
#
#                 if distance == decel_region or distance == max_velocity_region or distance == accel_region:
#                     break
#
#             time_output = t
#             time_list.append(time_output)
#             time_dict[j] = time_output
#     print("max_vel_count = ", count)
#     print("flag count = ", flag_count)
#     return time_dict
#
#
# time_dict = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_commands_dict )
# start_delay_time = float(distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel,[start_delay])[0])
# offset_time = float(distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, [abs(offset)])[0])
#
# if offset < 0:
#     offset_time = -offset_time
#
# #offset_time = offset/feed
#
# calc_time_end = time.time()
# print("start_delay_time = ", start_delay_time, "\noffset_time = ", offset_time)
# print("length of distance2time = ", calc_time_end-calc_time_start)
#
# final_dict_start = time.time()
# ## creates final dictionaries of commands and times to use
# def final_dicts(time_dict):
#     command_list = []
#     time_based_dict_final = {}
#     command_dict_final = {}
#
#     count_t = 0
#     dict_count_t = 0
#     start_count_c = 0
#     initial_commands = []
#     initial_commands_trigger = 0
#     for i in range(len(time_dict)):
#         entry = time_dict[i]
#         dict_count_c = dict_count_t
#         if type(entry) != str:
#             time_based_dict_final[dict_count_t] = entry
#             command_list = []
#             count_t += 1
#             start_count_c = 0
#             initial_commands_trigger = 1
#         else:
#             command_list.append(entry)
#             if initial_commands_trigger == 0:
#                 initial_commands = command_list
#             else:
#                 command_dict_final[dict_count_c] = command_list
#                 if start_count_c == 0:
#                     dict_count_t += 1
#                     start_count_c = 1
#
#     for i in range(len(command_dict_final)):
#         command_list = command_dict_final[i]
#         command_dict_final[i] = '[%s]' % ', '.join(map(str, command_list))
#
#     # print("time_based_dict_unsummed = ", time_based_dict_unsummed)
#     # print("time_based_dict_final = ", time_based_dict_final)
#     # print("command_dict_final = ", command_dict_final)
#     # print("initial_commands = ", initial_commands )
#     return time_based_dict_final, command_dict_final, initial_commands
# final_dicts_output = final_dicts(time_dict)
# time_based_dict_final = final_dicts_output[0]
# command_dict_final = final_dicts_output[1]
# initial_commands = final_dicts_output[2]
#
# set_press = '[%s]' % ', '.join(map(str,initial_commands[:number_of_ports_used]))
# initial_toggle ='[%s]' % ', '.join(map(str, initial_commands[number_of_ports_used:]))
# final_dict_end = time.time()
# print("length of final_dicts = ", final_dict_end - final_dict_start)
#
# end_time = time.time()
# total_time = end_time - start_time
# print("\nTime to translate distance to time: ", total_time)
#
# print("time_based_dict_final = ", time_based_dict_final)
# # print("set_press: ", set_press)
# # print("initial_toggle: ", initial_toggle)
# # print("command_dict_final = ", command_dict_final)
#
# with open("DGC_Time_based_variables.py", "a") as f:
#     f.write('\r\n#----------------------------')
#     f.write('\r\n#date and time: ' + dt_string)
#     f.write('\rfeed = ' + str(feed) + '\raccel = ' + str(accel) + '\rdecel = ' + str(decel))
#     f.write('\rtesting =  "' + testing + '"')
#     f.write('\rgcode_txt_imported = "' + gcode_txt_imported + '"')
#     f.write('\rfinal_gcode_txt_export = "' + final_gcode_txt_export + '"')
#     f.write('\rstart_delay_time = ' + str(start_delay_time) + "\roffset_time = " + str(offset_time))
#     # f.write('\rZ_var = "' + Z_var + '"' + '\rz_height = ' + str(z_height))
#     f.write('\rset_press = "' + str(set_press) + '"')
#     f.write('\rinitial_toggle = "' + str(initial_toggle)+ '"')
#     f.write('\rtime_based_dict_final = ' + str(time_based_dict_final))
#     f.write('\rcommand_dict_final = ' + str(command_dict_final))




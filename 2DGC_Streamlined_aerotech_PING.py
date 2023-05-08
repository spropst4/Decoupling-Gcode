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
testing = "PING" #"quick summary"

gcode_txt_imported = "1DGC_Generate_Checkerboard_M1.txt"
final_gcode_txt_export = "1DGC_Generate_Checkerboard_M1_aerotech.txt"

number_of_ports_used = 1 # (aka number of materials used)
resync_type = 'command-based' # direction-based OPTIONS: 'command-based', 'direction-based', False
resync_number = 20 # number of directions changes between resyncing

Z_var = "D"
z_height = 1
z_o= -150 + z_height

home = False  #do you want to home it? (True = yes)

# Open the port for the python-hyrel connection

# Open the ports for the pressure box
# press_com1 = 4 # core
# press_com2 = 5 # shell
#
# serialPort1 = openport(press_com1)
# serialPort2 = openport(press_com2)
#
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
# print(gcode_list)
print("Translating Gcode to Time....")

## splits up gcode into directions, distances, G command type (G1, G2, G3, etc)
## create a gcode,  distance, and direction dictionary
start = time.time()
def parse_gcode(gcode_list):

    ## Finds G-command (i.e., G1, G2, G3)
    def find_G(gcode_dict):  # s = string to search, ch = character to find
        for elem in enumerate(gcode_dict):
            if "G" in elem[1]:
                return True, elem[1] # finds location of character, strips it, and outputs numerical number
        else:
            return False, elem[1]

    def find_distances(gcode_dict, ch):  # s = string to search, ch = character to find
        # ch = character to find
        result = 0,0
        for elem in enumerate(gcode_dict):
            if ch in elem[1]:
                result = float(elem[1].strip(ch)), ch # finds location of character, strips it, and outputs numerical number
                break

        return result

    ## pythag thm
    def pythag(x, y, z):
        return (sqrt(abs(float(x)) ** 2 + abs(float(y)) ** 2 + abs(float(z)) ** 2))

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
    distance_commands_dict = {}
    slope_dict = {}
    count = 0
    for i in range(len(gcode_list)):
        gcode_dict[i] = gcode_list[i].split(" ")

        ## Stores type of G-command for each line
        # G_command_dict[i] = find_G(gcode_dict[i], "G")

        find_G_result = find_G(gcode_dict[i])

        ## Stores distance values for each command
        find_X = find_distances(gcode_dict[i], "X")
        find_Y = find_distances(gcode_dict[i], "Y")
        find_Z = find_distances(gcode_dict[i], "Z")
        find_I = find_distances(gcode_dict[i], "I")
        find_J = find_distances(gcode_dict[i], "J")

        if find_G_result[0] == True:
            G_command_dict[count] = find_G_result[1]
            X_dist_dict[count] = find_X[0]
            Y_dist_dict[count] = find_Y[0]
            Z_dist_dict[count] = find_Z[0]
            I_dist_dict[count] = find_I[0]
            J_dist_dict[count] = find_J[0]

            All_dist_dict[count] = [X_dist_dict[count], Y_dist_dict[count], Z_dist_dict[count], I_dist_dict[count], J_dist_dict[count]]
            All_var_dict[count] = [find_X[1], find_Y[1], find_Z[1], find_I[1], find_J[1]]

            ### Linear Commands
            direction_check = []
            if G_command_dict[count] == 'G1':
                distance = pythag(X_dist_dict[count], Y_dist_dict[count], Z_dist_dict[count])
                for elem in All_var_dict[count]:
                    if elem != 0:
                        direction_check.append(elem)
                        # direction_dict[count].append(elem)

                if "X" in direction_check and "Y" in direction_check and "Z" not in direction_check:
                    slope = Y_dist_dict[count]/X_dist_dict[count]
                else:
                    slope = False

                slope_dict[count] = slope

            ### Circular commands
            elif G_command_dict[count] == 'G3' or 'G03':
                theta = find_theta(X_dist_dict[count], Y_dist_dict[count], I_dist_dict[count], J_dist_dict[count])
                if theta <= 0:
                    theta = 2 * np.pi - abs(theta)
                R = pythag(I_dist_dict[count], J_dist_dict[count], 0)
                arc_length = R * theta
                distance = arc_length

                slope_dict[count] = False


            elif G_command_dict[count] == 'G2' or 'G02':
                theta = find_theta(X_dist_dict[count], Y_dist_dict[count], I_dist_dict[count], J_dist_dict[count])
                if theta < 0:
                    theta = abs(theta)
                else:
                    theta = 2 * np.pi - theta
                R = pythag(I_dist_dict[count], J_dist_dict[count], 0)
                arc_length = R * theta
                distance = arc_length

                slope_dict[count] = False

            count += 1
            distance_commands_dict[i] = distance


        else:
            command = find_G_result[1]
            distance_commands_dict[i] = command


    # print(gcode_dict)
    # print(G_command_dict)
    # print(X_dist_dict)
    # print(Y_dist_dict)
    # print(Z_dist_dict)
    # print(I_dist_dict)
    # print(J_dist_dict)
    # print(All_dist_dict)
    # print(All_var_dict)
    # print(slope_dict)
    # print(distance_commands_dict)

    return gcode_dict, G_command_dict, X_dist_dict, Y_dist_dict, Z_dist_dict, I_dist_dict, J_dist_dict, All_dist_dict, All_var_dict, slope_dict, distance_commands_dict
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
slope_dict = parse_output[9]
distance_commands_dict = parse_output[10]

print("distance_commands_dict = ", distance_commands_dict)
print("time to parse_gcode = ", time.time() - start)

## Combines "like" gcode lines into a continuous path (used to create final gcode and acceleration path)
start = time.time()
def condense_gcode(resync_number, resync_type, distance_commands_dict,G_command_dict, All_var_dict, X_dist_dict, Y_dist_dict, Z_dist_dict, I_dist_dict, J_dist_dict):
    ## pythag thm
    def pythag(x, y, z):
        return (sqrt(abs(float(x)) ** 2 + abs(float(y)) ** 2 + abs(float(z)) ** 2))
    ## find arc_angle
    def find_theta(X, Y, I, J):  # finds angle between intersecting lines
        import math
        from math import atan2
        a = math.atan2(-J, -I)
        b = math.atan2(Y - J, X - I)
        theta = b - a
        return theta

    dir_change_count = 0
    X_sum = X_dist_dict[0]
    Y_sum = Y_dist_dict[0]
    Z_sum = Z_dist_dict[0]
    I_0 = I_dist_dict[0]
    J_0 = J_dist_dict[0]

    Sum_G_command_dict = {0: G_command_dict[0]}
    Sum_var_dict = {0: All_var_dict[0]}
    Sum_coord_dict = {0: [X_dist_dict[0], Y_dist_dict[0], I_dist_dict[0], J_dist_dict[0]]}

    ### Finds initial distances....
    if G_command_dict[0] == "G1":
        sum_distance = pythag(X_sum, Y_sum, Z_sum)
    #### for circles
    else:
        theta = find_theta(X_sum, Y_sum, I_0, J_0)
        if G_command_dict[0] == "G3":
            if theta <= 0:
                theta = 2 * np.pi - abs(theta)
        else:
            theta = find_theta(X_sum, Y_sum, I_0, J_0)
            if theta < 0:
                theta = abs(theta)
            else:
                theta = 2 * np.pi - theta

        R = pythag(I_0, J_0, 0)
        sum_distance = R * theta

    Sum_distance_dict = {0:sum_distance}

    resync_trigger_distance_dict = {}            # dictionary that keeps track of where direction changes occur (use to trigger a resync after N number of direction changes). ex: if key = 12, the direction changes between keys 12 and 13 in distance_commands_dict
    resync_trigger_numCommand_dict = {}          # dictionary that keeps track of where commands occur (use to trigger a resync after N number of commands). ex: if key = 1, key = 1 in distance_commands_dict is aux command
    command_count = 0
    i = 0 # count for number of times a distance command is used

    for j in range(len(distance_commands_dict)):
        type_check = type(distance_commands_dict[j])
        if type_check == str:
            command_count +=1
            #resync_trigger_numCommand_dict[j] = command_count
            #resync_trigger_numCommand_dict[command_count] = j

            if command_count%resync_number == 0 and resync_type == 'command-based':
                # resync_trigger_numCommand_dict[command_count] = j
                resync_trigger_numCommand_dict[j] = command_count

        if type_check != str and i < len(G_command_dict) - 1:
            i +=1
            current_G_command = G_command_dict[i]
            current_var = All_var_dict[i]
            ## Combines "like" gcode lines into a continuous path
            if G_command_dict[i] == G_command_dict[i - 1] and All_var_dict[i] == All_var_dict[i - 1] and slope_dict[i] == slope_dict[i-1]:
                # '''G1 Commands'''
                if current_G_command == "G1":
                    X_sum += X_dist_dict[i]
                    Y_sum += Y_dist_dict[i]
                    Z_sum += Z_dist_dict[i]

                # '''G2/G3 Commands'''
                elif (round(I_dist_dict[i], 9) == round(I_dist_dict[i-1] - X_dist_dict[i-1]), 9) and (round(J_dist_dict[i], 9) == round(J_dist_dict[i-1] - Y_dist_dict[i-1]), 9):
                    X_sum += X_dist_dict[i]
                    Y_sum += Y_dist_dict[i]
                    print("X_sum = ", X_sum)
                    if round(X_sum, 9) == 0:
                        X_sum = 0
                    if round(Y_sum, 9) == 0:
                        Y_sum = 0

                else: # if it is not a continuous circle
                    dir_change_count += 1
                    X_sum = X_dist_dict[i]
                    Y_sum = Y_dist_dict[i]
                    Z_sum = Z_dist_dict[i]
                    I_0 = I_dist_dict[i]  # I value is always referenced from starting point
                    J_0 = J_dist_dict[i]  # J value is always referenced from starting point


                    if dir_change_count%resync_number == 0 and resync_type == 'direction-based':
                        resync_trigger_distance_dict[j] = dir_change_count
                        #resync_trigger_distance_dict[dir_change_count] = j
                    elif resync_type == 'command-based':
                        resync_trigger_distance_dict[j] = dir_change_count
                        #resync_trigger_distance_dict[dir_change_count] = j

            else:
                dir_change_count += 1
                X_sum = X_dist_dict[i]
                Y_sum = Y_dist_dict[i]
                Z_sum = Z_dist_dict[i]
                I_0 = I_dist_dict[i]  # I value is always referenced from starting point
                J_0 = J_dist_dict[i]  # J value is always referenced from starting point

                if dir_change_count % resync_number == 0 and resync_type == 'direction-based':
                    resync_trigger_distance_dict[j] = dir_change_count
                    # resync_trigger_distance_dict[dir_change_count] = j
                elif resync_type == 'command-based':
                    resync_trigger_distance_dict[j] = dir_change_count
                    # resync_trigger_distance_dict[dir_change_count] = j

            ### Finds total distances that will be used in acceleration profile
            if current_G_command == "G1":
                sum_distance = pythag(X_sum, Y_sum, Z_sum)

            #### for circles
            else:
                theta = find_theta(X_sum, Y_sum, I_0, J_0)
                if current_G_command == "G3":
                    if theta <= 0:
                        theta = 2 * np.pi - abs(theta)
                else:
                    theta = find_theta(X_sum, Y_sum, I_0, J_0)
                    if theta < 0:
                        theta = abs(theta)
                    else:
                        theta = 2 * np.pi - theta

                R = pythag(I_0, J_0, 0)
                sum_distance = R * theta


            Sum_G_command_dict[dir_change_count] = current_G_command # for writing condensed gcode
            Sum_var_dict[dir_change_count] = current_var # for writing condensed gcode
            Sum_coord_dict[dir_change_count] = [X_sum, Y_sum, Z_sum, I_0, J_0] # for writing condensed gcode
            Sum_distance_dict[dir_change_count] = sum_distance # for writing acceleration profile

    resync_trigger_distance_dict_2 = {} # to use when command-based
    for key in resync_trigger_numCommand_dict:
        loop = True
        i = 0
        while True:
            try:
                test = resync_trigger_distance_dict[key + i]
                break
            except KeyError:
                test = []
            try:
                test = resync_trigger_distance_dict[key - i]
                i = -i
                break
            except KeyError:
                test = []

            i += 1
        resync_trigger_distance_dict_2[key + i] = resync_trigger_distance_dict[key + i]

    if resync_type == 'command-based':
        resync_trigger_distance_dict = resync_trigger_distance_dict_2

    # print(Sum_G_command_dict) # G-commands
    # print(Sum_var_dict) # variables, X, Y, Z....
    #print(Sum_coord_dict) # coordinate values
    # print(Sum_distance_dict)
    print("reset based on number of commands: ", resync_trigger_numCommand_dict)
    print("reset based on distance: ", resync_trigger_distance_dict)


    return Sum_G_command_dict, Sum_var_dict, Sum_coord_dict, Sum_distance_dict, resync_trigger_distance_dict, resync_trigger_numCommand_dict
condense_results = condense_gcode(resync_number, resync_type, distance_commands_dict, G_command_dict, All_var_dict,
                                  X_dist_dict, Y_dist_dict, Z_dist_dict, I_dist_dict, J_dist_dict)
Sum_G_command_dict = condense_results[0]
Sum_var_dict = condense_results[1]
Sum_coord_dict = condense_results[2]
Sum_distance_dict = condense_results[3]
reset_trigger_distance_dict = condense_results[4]
reset_trigger_numCommand_dict = condense_results[5]
print("time to condense_gcode = ", time.time() - start)

start = time.time()
def generate_gcode(final_gcode_txt_export, accel, Z_var, z_o, feed, Sum_G_command_dict, Sum_var_dict, Sum_coord_dict, resync_number):
    # create txt for gcode used in 3d printer
    resync_PING = ('\n$hFile = FILEOPEN "COM'+str(port_python) +'", 2\nCOMMINIT $hFile, "baud=115200 parity=N data=8 stop=1"\nCOMMSETTIMEOUT $hFile, -1, -1, 1000\n\rFILEWRITE $hFile, "start1"')

    with open(final_gcode_txt_export, "w") as f:
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
        f.write(resync_PING)
        f.write('\nG4 P3\n\r')

        for i in range(len(Sum_coord_dict)):
            G_command = Sum_G_command_dict[i]
            if G_command == "G3":
                G_command = "CCW"
            if G_command == "G2":
                G_command = "CW"
            coordinates = str(G_command) + " "
            for j in range(len(Sum_coord_dict[i])):
                dist = Sum_coord_dict[i][j]
                variable = Sum_var_dict[i][j]
                if variable != 0 :
                    coordinates += str(variable) + str(dist) + " "

            f.write("\n\r" + coordinates)


            f.write(resync_PING)

        f.write('\n\rFILECLOSE $hFile\nM02')
    print("\n", final_gcode_txt_export, "has been created\n\r")
    return f

generate_gcode(final_gcode_txt_export, accel, Z_var, z_o, feed, Sum_G_command_dict, Sum_var_dict, Sum_coord_dict, resync_number)
print("time to generate_gcode = ", time.time() - start)

## creates acceleration profile
start = time.time()
def accel_profile(Sum_distance_dict):
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

    for i in range(len(Sum_distance_dict)):
        if accel == 0:
            steady_state_dist = abs(Sum_distance_dict[i])
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

            steady_state_dist = abs(Sum_distance_dict[i]) - accel_dist - decel_dist


        if steady_state_dist <= 0:
            steady_state_dist = 0
            accel_dist = abs(Sum_distance_dict[i]) * 0.5
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
accel_profile_output = accel_profile(Sum_distance_dict)
accel_profile_distance = accel_profile_output[0]
accel_profile_time = accel_profile_output[1]
print("time to create accel_profile = ", time.time() - start)

## creates dictionary of time and commands
start = time.time()
def distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_commands_dict):
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
    for j in range(len(distance_commands_dict)):
        if type(distance_commands_dict[j]) == str:
            time_dict[j] = distance_commands_dict[j]
        else:
            distance += abs(distance_commands_dict[j])
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
    # print("max_vel_count = ", count)
    # print("flag count = ", flag_count)
    return time_dict
time_dict = distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, distance_commands_dict)
start_delay_time = float(
    distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, [start_delay])[0])
offset_time = float(distance2time(accel_profile_distance, accel_profile_time, feed, accel, decel, [abs(offset)])[0])

if offset < 0:
    offset_time = -offset_time

#offset_time = offset/feed

print("time to create distance2time = ", time.time() - start)

start = time.time()
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
print("time to create final_dicts = ", time.time() - start)

end_time = time.time()
total_time = end_time - start_time
print("\nTotal time to translate distance to time: ", total_time)

print("set_press: ", set_press)
print("initial_toggle: ", initial_toggle)
print("time_based_dict_final = ", time_based_dict_final)
print("command_dict_final = ", command_dict_final)


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
#
#             if message == "start1\r\n":
#                 pause = 0.011305268287658692#from AEROTECH_PING_data.txt
#
#                 exec(set_press)
#                 print("Setting the pressures....")
#
#                 break
#
# #### Executes Absolute timing ####
# print("Executing time-based code....")
# time.sleep(3-pause - start_delay_time)
#
# i = 0
# exec(initial_toggle)
# start_time = time.time()
# time_dict_list = []
# error_list = []
# real_time_list = []
# while (i < len(command_dict_final)):
#     current_time_stamp = time_based_dict_final[i] - offset_time
#     # if i == 0:
#     #     current_time_stamp = current_time_stamp - start_offset_time
#     real_time = time.time() - start_time
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


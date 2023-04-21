'''
This code is used to calculate how long it takes to travel a specified distance depending on the number of actions in that distance (using traditional G-code).
'''

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
            # x_steady = round(x_steady, 10)
        except TypeError:
            print("error in value of x; it may be imaginary")

    find_t = v_0 + accel * t - v_f  # finds time to steady state velocity
    sol_t = solve(find_t)
    t_steady = sol_t[0]
    # t_steady = round(t_steady, 10)
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

accel = 200
decel = -accel

velocity = 20

total_distance = 100                                   # total distance to travel
smallest_distance_between_commands = 0.1               # smallest distance between commands to test

min_number_of_commands = 0
max_number_of_commands = total_distance / smallest_distance_between_commands
print(max_number_of_commands/10)

total_times_list = []
number_commands_list = []
data_all = []

accel_length_results = accel_length(0, velocity, accel)
accel_distance = accel_length_results[0]

accel_time = accel_length_results[1]
decel_time = accel_time


number_commands_to_test = min_number_of_commands
while number_commands_to_test <= max_number_of_commands:

    if number_commands_to_test == 0:
        distance_to_test = total_distance
    else:
        distance_to_test = total_distance/number_commands_to_test

    steady_distance = distance_to_test - 2 * accel_distance
    steady_time = steady_distance/velocity
    one_profile_time = accel_time + steady_time + decel_time

    if accel_distance*2 > distance_to_test:
        accel_time_low = findt(0, accel, distance_to_test / 2)
        decel_time_low = accel_time
        # print(accel_time_low)
        one_profile_time = accel_time_low + decel_time_low

    total_time = one_profile_time*(total_distance / distance_to_test)

    number_commands_list.append(number_commands_to_test)
    total_times_list.append(total_time)
    data_all.append([number_commands_to_test, total_time])

    number_commands_to_test += 10

print(data_all)
print(total_distance/number_commands_to_test)
print(one_profile_time)
print(accel_time)
print(accel_distance)

#importing library
import csv
#
# # opening the csv file in 'w' mode
# file = open('effect_of_numCommands_varyFeed_V2.csv', 'w+', newline='')
#
# with file:
#     #identifying header
#
#     header = ["number of commands per "+ str(total_distance) + " mm", "total time (s)", "velocity = " + str(velocity), "acceleration = " + str(accel)]
#     writer = csv.writer(file)
#
#     writer.writerows([' ', ' '])
#
#     writer = csv.DictWriter(file, fieldnames=header)
#     writer.writeheader()
#     file.close()
#
# file = open('effect_of_numCommands_varyFeed_V2.csv', 'a+', newline='')
# with file:
#     writer = csv.writer(file)
#     writer.writerows(data_all)

from csv import writer
from csv import reader

# Open the input_file in read mode and output_file in write mode
with open('effect_of_numCommands_varyAccel_V2.csv', 'r') as read_obj:
    # Create a csv.reader object from the input file object
    csv_reader = reader(read_obj)
    # Read each row of the input csv file as list
    count = 0
    header = True
    update_data = []
    for row in csv_reader:
        prev_list = row
        # Append the default text in the row / list
        if header == True:
            prev_list.append("a = " + str(accel))
            update_data.append(prev_list)
            header = False
            labels = True
        elif labels == True:
            prev_list.append("total time (s)")
            update_data.append(prev_list)
            labels = False
        else:
            prev_list.append(total_times_list[count])
            update_data.append(prev_list)
            count += 1

print(update_data)
print(count)
print(len(total_times_list))

read_obj.close()

file = open('effect_of_numCommands_varyAccel_V2.csv', 'w', newline='')
with file:
    writer = csv.writer(file)
    writer.writerows(update_data)

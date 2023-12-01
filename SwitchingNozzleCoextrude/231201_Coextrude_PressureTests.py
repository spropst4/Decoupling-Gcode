def write_setpress_Automation1(com, pressure, dwell): # com as list, pressure as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecSetPressure(' + str(com) + ', ' + str(pressure) + ')")' #+ '\nDwell(' +str(dwell) + ')'

def write_togglepress_Automation1(com, dwell): # com as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecTogglePressure(' + str(com) + ')")' #+ '\nDwell('+str(dwell) + ')'

def write_valves_Automation1(valve, command): # valve as integar
    global ON
    global OFF
    return '\n$OutBits[' + str(valve) + '] =' + str(command)

def socketwrite(command_list):
    string = '\nSocketWriteString($clientSocket, "'
    for elem in command_list:
        string += elem
    return string


com = [8,9]
valve = [6, 7]
pressure_start = [21.5, 21.5]
pressure_end = [16.5, 26.5]
increment = 0.5

x_length = 150
y_length = 3


if pressure_start[0] < pressure_end[0]:
    increment_1 = 0.5
    increment_2 = -0.5
else:
    increment_1 = -0.5
    increment_2 = 0.5

sign = 1
current_pressure1 = pressure_start[0]
current_pressure2 = pressure_start[1]
current_pressure = [current_pressure1, current_pressure2]

print(write_setpress_Automation1(com, current_pressure, 0))
print(write_togglepress_Automation1(com, 0))
for elem in valve:
    print(write_valves_Automation1(elem, 1))

while current_pressure1 != (pressure_end[0]):
    current_pressure1 += increment_1
    current_pressure2 += increment_2
    current_pressure = [current_pressure1, current_pressure2]
    print('G1 X' + str(sign*x_length))
    for elem in valve:
        print(write_valves_Automation1(elem, 0))

    print(write_setpress_Automation1(com, current_pressure, 0))

    print('G1 Y' + str(y_length))
    for elem in valve:
        print(write_valves_Automation1(elem, 1))

    sign = -sign




def write_setpress_Automation1(com, pressure, dwell): # com as list, pressure as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecSetPressure(' + str(com) + ', ' + str(pressure) + ')")' + '\nDwell(' +str(dwell) + ')'

def write_togglepress_Automation1(com, dwell): # com as list, dwell as real
    return '\nSocketWriteString($clientSocket, "\\nexecTogglePressure(' + str(com) + ')")' + '\nDwell(' +str(dwell) + ')'


print(write_setpress_Automation1([3], [4], 0.15))
print(write_togglepress_Automation1([3], 0.15))
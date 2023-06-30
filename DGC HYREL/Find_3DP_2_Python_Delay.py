def openport(port):
    # IMPORTS
    import serial
    baudrate = 115200
    bytesize = 8
    timeout = 2

    return serial.Serial("COM" + str(port), baudrate=baudrate, bytesize=bytesize, timeout=timeout, stopbits=serial.STOPBITS_ONE)
import time
from datetime import datetime
from datetime import date
now = datetime.now() # datetime object containing current date and time
current_date = date.today()
Date = now.strftime("%y%m%d")     # dd/mm/YY H:M:S


##### Test Information
Title = "Time delay between Hyrel M792 and python."
Name = "SPropst"

port_python = 1 # create a virtual port; e.g. if com1 <--> com2, set port on python to 1 and select port 2 on the Hyrel (or vice versa)

pause = 0.5
###### WAITING FOR PING ##################################
print("Waiting for ping to start....")
if __name__ == '__main__':

    ser = openport(port_python)
    ser.reset_input_buffer()

    start_time = time.time()
    delta_list = []
    delay_list = []
    message = "message"
    while True:
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            ping_time = time.time()
            delta = ping_time - start_time
            start_time = ping_time
            delay = delta-pause

            print('\r\n------------------')
            print('Delta = ', delta)
            print('Delay from ' + str(pause) + ' second(s) = ', delay)
            message = ser.read(bytesToRead)  # creates type bytes, e.g., b'M792 ;SEND message\n'
            message = message.decode(encoding='utf-8')  # creates type string, e.g., 'M792 ;SEND message\n'
            print('Received command: ' + message)

            delta_list.append(delta)
            delay_list.append(delay)

        if message == "end\n":
            break

        #break

import numpy as np

std_delta = np.std(delta_list[1:])
avg_delta = np.average(delta_list[1:])

std_delay = np.std(delay_list[1:])
avg_delay = np.average(delay_list[1:])

print("std delta = ", std_delta)
print("average delta = ", avg_delta)
print("std delay = ", std_delay)
print("average delay = ", avg_delay)

with open("Find_3DP_2_Python_delay_data_" + Date + ".txt", "w") as f:
    f.write(Title)
    f.write('\r' + Date)
    f.write('\r' + Name)
    f.write('\r\nIdeal pause between commands (sec): pause = ' + str(pause))
    f.write("\r\n -------- Raw Data --------")
    f.write("\rnum_data_points = " + str(len(delay_list)))
    f.write("\rdelta_list = " + str(delta_list))
    f.write("\rdelay_list = " + str(delay_list))

    f.write("\r\n -------- Calculated Stats --------")
    f.write("\ravg_delta = " +str(avg_delta))
    f.write("\rstd_delta = " + str(std_delta))
    f.write("\r\navg_delay = " +str(avg_delay))
    f.write("\rstd_delay = " + str(std_delay))

    f.write("\r\n -------- NOTES --------")
    f.write("\rRemove the first data point in delta_list and delay_list, which is the time from starting the python and the first ping.")
    f.write("\rdelta: time between consecutive commands (excludes first data point in list)")
    f.write("\rdelay: difference between ideal time and delta (excludes first data point in list)")

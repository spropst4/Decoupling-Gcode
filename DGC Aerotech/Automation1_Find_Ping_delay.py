import socket
from threading import Thread
import time
def thread_make_list(data):
    # if data != b'':
    global list_data
    list_data.append(data)
    #return list_data
def thread_exec_data():
    global list_data
    global decoded_data
    if list_data != []:
        decoded_data = list_data[0].decode("utf-8")
        list_data.remove(list_data[0])
    #return list_data


export_data_file = '231114_Automation1_FindDelay_data'
Title = "Time delay between Automation1 TCP and python."
Date = "11/14/2023"
Name = "Sarah Propst"

pause = 0.5

###### WAITING FOR PING ##################################
print("Waiting for ping to start....")
if __name__ == '__main__':
    HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
    PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
    list_data = []

    start_time = time.time()
    delta_list = []
    delay_list = []
    decoded_data = ' '
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        conn, addr = s.accept()
        with conn:
            print(f"Connected by {addr}")
            while decoded_data != 'END':
                data = conn.recv(1024)


                ping_time = time.time()
                delta = ping_time - start_time
                start_time = ping_time
                delay = delta - pause

                print('\r\n------------------')
                print('Delta = ', delta)
                print('Delay from ' + str(pause) + ' second(s) = ', delay)
                Thread(target=thread_make_list(data)).start()
                Thread(target=thread_exec_data()).start()
                print('Received command: ' + decoded_data)

                delta_list.append(delta)
                delay_list.append(delay)

                # if decoded_data == 'END':
                #     False

                conn.sendall(data)


import numpy as np

std_delta = np.std(delta_list[1:])
avg_delta = np.average(delta_list[1:])

std_delay = np.std(delay_list[1:])
avg_delay = np.average(delay_list[1:])

print("std delta = ", std_delta)
print("average delta = ", avg_delta)
print("std delay = ", std_delay)
print("average delay = ", avg_delay)

with open(export_data_file+'_P'+str(pause)+ '_NumData'+str(len(delay_list[1:])), "w") as f:
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


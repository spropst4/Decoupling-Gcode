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
dt_string = now.strftime("%d/%m/%Y")     # dd/mm/YY H:M:S

port_python = 1

Title = "How much time does a resync ping add to total print time? (30 x 30; y = 1 mm)"
Sample = 'No_Resync_5' #"Resync_every_dir_change_5" #'No_Resync_2'


###### WAITING FOR PING ##################################
print("Waiting for ping to start....")
if __name__ == '__main__':

    ser = openport(port_python)
    ser.reset_input_buffer()

    start_time = time.time()
    time_stamps_from_aerotech = []
    python_received_time_stamps = []
    timer_list = []
    message = "message"
    prev_message = 0
    while True:
        bytesToRead = ser.inWaiting()
        if bytesToRead > 0:
            python_recieved_time = time.time() - start_time
            print('\r\n------------------')
            message = ser.read(bytesToRead)  # creates type bytes, e.g., b'M792 ;SEND message\n'
            message = message.decode(encoding='utf-8')  # creates type string, e.g., 'M792 ;SEND message\n'
            if message == "start\r\n":
                start_time = time.time()
            elif message == "end\r\n":
                break
            else:
                message = float(message.strip('\r\n')) / 1000
                print('aerotech time stamp t = ', message)
                time_stamps_from_aerotech.append(message)
                python_received_time_stamps.append(python_recieved_time)



import numpy as np
with open(now.strftime("%Y%m%d")+'_resync_data.txt', 'a') as f:
    #f.write('\n' + Title)
    f.write('\n' + Sample)
    #f.write('\r' + dt_string)
    f.write("\r\n -------- Raw Data --------")
    f.write("\rtime_stamps_from_aerotech_" + Sample + " = " + str(time_stamps_from_aerotech))
    f.write("\rpython_received_time_stamps_" + Sample + " = " + str(python_received_time_stamps))
    f.write("\r--------------------------------------------------------------------------------\r")

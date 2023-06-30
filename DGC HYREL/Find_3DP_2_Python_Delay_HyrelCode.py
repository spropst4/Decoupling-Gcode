'''
230629: This code repeats the M792; SEND message 501 times. The code will be used by the hyrel to send pings to python in order to determine the delay.

Use code: Find_3DP_2_Python_Delay.py to recieve the pings from the Hyrel, calculate, and write a text file of the data
'''

repeat = 501 # 501 on because the first message is erroronous
pause = 0.5

for i in range(repeat):

    print("M792 ;SEND helllloooooooooooo testing 1, 2, 3...")
    print("G4 P" + str(pause *1000)) # Hyrel pause in ms

print("M792 ;SEND end")
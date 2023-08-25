import numpy as np
def find_theta(I, J, X, Y):
    ## finds angle between intersecting lines
    import math
    from math import atan2
    a = math.atan2(-J, -I)
    b = math.atan2(Y-J, X-I)
    theta = b - a
    return theta

'''
    G91
    G0 X4 Y3
    G3 X-1 Y1 I-4 J-3
    G3 X-7 Y-1 I-3 J-4
    G3 X-1 Y-3 I4 J-3
    
    G90
    G0 X0 Y0
    G91
    G0 X4 Y3
    G3 X-9 Y-3 I-4 J-3
'''
 
Gcommand1 = "G3"
X1 = -1
Y1 = 1
I1 = -4
J1 = -3


Gcommand2 = "G3"
I2 = -4 - (-1)
J2 = -3 - (1)
X2 = -7
Y2 = -1

Gcommand3 = "G3"
I3 = 4
J3 = -3
X3 = -1
Y3 = -3


''''
    G90
    G0 X0 Y0
    G91
    G0 X4 Y3
    G2 X-9 Y-3 I-4 J-3
    G2 X1 Y3 I5 J0
    G2 X7 Y1 I4 J-3
'''

Gcommand4 = "G2"
X4 = -9
Y4 = -3
I4 = -4
J4 = -3

Gcommand5 = "G2"
X5 = 1
Y5 = 3
I5 = 5
J5 = 0

Gcommand6 = "G2"
X6 = 7
Y6 = 1
I6 = 4
J6 = -3

Gcommand_list = [Gcommand1, Gcommand2, Gcommand3, Gcommand4, Gcommand5, Gcommand6]
X_list = [X1, X2, X3, X4, X5, X6]
Y_list = [Y1, Y2, Y3, Y4, Y5, Y6]
I_list = [I1, I2, I3, I4, I5, I6]
J_list = [J1, J2, J3, J4, J5, J6]

### calcuates arc length
arc_length_list = []
for i in range(len(Gcommand_list)):
    X = X_list[i]
    Y = Y_list[i]
    I = I_list[i]
    J = J_list[i]
    if Gcommand_list[i] == "G3" or "G03":
        theta =  find_theta(I, J, X, Y)
        if theta <= 0:
            theta = 2*np.pi - abs(theta)
        R = np.sqrt(I**2 + J**2)
        arc_length = R*theta
        arc_length_list.append(arc_length)
        
    elif Gcommand_list[i] == "G2" or "G02":
        theta =  find_theta(I, J, X, Y)
        if theta < 0:
            theta = abs(theta)
        else:
            theta = 2*np.pi - theta
        R = np.sqrt(I**2 + J**2)
        arc_length = R*theta
        arc_length_list.append(arc_length)

print(arc_length_list)
  
  
# ##### compiles Gcode      
# Xf = X_list[0]
# Yf = Y_list[0]
# I0 = I_list[0]
# J0 = J_list[0]
# Gcommand = Gcommand_list[0]  
# for i in range(1, len(Gcommand_list)):
#     print(i)
#     if Gcommand_list[i-1] == Gcommand_list[i] and I_list[i]==I_list[i-1]- X_list[i-1]:
#         Xf += X_list[i]
#         Yf += Y_list[i]
#         I = I0
#         J = J0
#     else:
#         print(Gcommand, " X",Xf," Y",Yf, " I",I, " J",J)
#         Xf = X_list[i]
#         Yf = Y_list[i]
#         I0 = I_list[i]
#         J0 = J_list[i]
#         Gcommand = Gcommand_list[i]

# print(Gcommand, " X",Xf," Y",Yf, " I",I, " J",J)

#print(Gcommand, " X",Xf," Y",Yf, " I",I, " J",J)
        
        
'''try next (concentric circles split into semi-circles)'''

circle_diam = 20
Gcommand_list = []
X_list = []
Y_list = []
I_list = []
J_list = []
i = 0
while circle_diam > 0:
    Y_list.append(0)
    J_list.append(0)
    Gcommand_list.append("G3")
    if i == 0: 
        X_list.append(-circle_diam)
        I_list.append(-circle_diam/2)
    elif (i+1)%2 != 0: ## odd lines
        circle_diam -= 2
        X_list.append(-circle_diam)
        I_list.append(-circle_diam/2)
    else:
        X_list.append(circle_diam)
        I_list.append(circle_diam/2)
    i += 1
##### compiles Gcode      
Xf = X_list[0]
Yf = Y_list[0]
I0 = I_list[0]
J0 = J_list[0]
Gcommand = Gcommand_list[0]  
for i in range(1, len(Gcommand_list)):
    if Gcommand_list[i-1] == Gcommand_list[i] and I_list[i]==I_list[i-1]- X_list[i-1]:
        Xf += X_list[i]
        Yf += Y_list[i]
        I = I0
        J = J0
        printed_command = False

    else:
        print(Gcommand, " X",Xf," Y",Yf, " I",I, " J",J)
        print("G0 X-1")
        Xf = X_list[i]
        Yf = Y_list[i]
        I0 = I_list[i]
        J0 = J_list[i]
        Gcommand = Gcommand_list[i]
        printed_command = True
if printed_command == False:
    print(Gcommand, " X",Xf," Y",Yf, " I",I, " J",J)
 
 
'''Outputs "traditional" gcode '''        
print("\r\r\n")
for i in range(len(Gcommand_list)):
    print(Gcommand_list[i], " X",X_list[i]," Y",Y_list[i], " I",I_list[i], " J",J_list[i])
    print('Switch materials')
    if (i+1)%2 == 0:
        print("G0 X-1")

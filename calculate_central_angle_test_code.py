
import math
from math import atan2

def method1_theta(I, J, x2, y2):
    a = math.atan2(-J, -I)
    b = math.atan2(y2-J, x2-I)
    theta = b - a
    return theta
 
def method2_theta(I, J, x2, y2):
    m1 = J/I
    m2 = (y2-J)/(x2-I)
    eq = (m2-m1)/(1+(m1*m2))
    theta = math.atan(eq) 
    return theta
    

##### Example 1:
print("\n\rEXAMPLE 1: ")

### Green and blue in Q1
I = -4
J = -3

x2 = -2
y2 = 3

Ex1_method1_Q1 = method1_theta(I, J, x2, y2)
print("Q1 method 1: for G2: theta = ", Ex1_method1_Q1)
print("for G3: theta = ", 2*math.pi - Ex1_method1_Q1)

# Ex1_method2_Q1 = method2_theta(I, J, x2, y2)
# print("Q1 method 2: for G2: theta = ", Ex1_method2_Q1)

##############################
### Purple and red in Q3

I2 = 4
J2 = 3

x22 = 2
y22 = -3

Ex1_method1_Q3 = method1_theta(I2, J2, x22, y22)
print("Q3 method 1: for G2: theta = ", Ex1_method1_Q3)
print("for G3: theta = ", 2*math.pi - Ex1_method1_Q3)

# Ex1_method2_Q1 = method2_theta(I2, J2, x22, y22)
# print("Q3 method 2: for G2: theta = ",Ex1_method2_Q1)

##### Example 2: 
print("\n\rEXAMPLE 2: ")
### Green and blue in Q1 (I and J taken from example 1)

I_ex2 = I - x2
J_ex2 = J - y2

x2_ex2 = -x2
y2_ex2 = -y2

Ex2_method1 = method1_theta(I_ex2, J_ex2, x2_ex2, y2_ex2)
print("method 1: for G2: theta = ", Ex2_method1)
print("method 1: for G2: theta_central = ", 2*math.pi + Ex2_method1)
print("method 1: for G3: theta = ", abs(Ex2_method1)) 


# Ex2_method2 = method2_theta(I_ex2, J_ex2, x2_ex2, y2_ex2)
# print("method 2: for G2: theta_acute = ", Ex2_method2)
# print("method 2: for G2: theta_central = ", 2*math.pi + Ex2_method2)

##### Example 3: 
print("\n\rEXAMPLE 3: ")
### (I and J taken from example 1)

I_ex3 = I
J_ex3 = J

x2_ex3 = -6
y2_ex3 = 3

Ex3_method1 = method1_theta(I_ex3, J_ex3, x2_ex3, y2_ex3)
print("method 1: for G2: theta = ", Ex3_method1)
print("method 1: for G3: theta = ", 2*math.pi - abs(Ex3_method1)) 


# Ex3_method2 = method2_theta(I_ex3, J_ex3, x2_ex3, y2_ex3)
# print("method 2: for G2: theta = ", Ex3_method2)

##### Example 3b: 
print("\n\rEXAMPLE 3b: switching start and finishing points ")
I_ex3b = I_ex3 - x2_ex3
J_ex3b = J_ex3 - y2_ex3

x2_ex3b = -x2_ex3
y2_ex3b = -y2_ex3
Ex3b_method1 = method1_theta(I_ex3b, J_ex3b, x2_ex3b, y2_ex3b)
print("method 1: for G2: theta = ", Ex3b_method1)
print("method 1: for G2: theta_central = ", 2*math.pi + Ex3b_method1)
print("method 1: for G3: theta = ", abs(Ex3b_method1)) 

# Ex3b_method2 = method2_theta(I_ex3b, J_ex3b, x2_ex3b, y2_ex3b)
# print("method 1: for G2: theta = ", Ex3b_method2)
# print("method 1: for G2: theta_central = ", 2*math.pi + Ex3b_method2)

##### Example 4: 
print("\n\rEXAMPLE 4: ")

### (I and J taken from example 1)

I_ex4 = I
J_ex4 = J

x2_ex4 = -8
y2_ex4 = -1

Ex4_method1 = method1_theta(I_ex4, J_ex4, x2_ex4, y2_ex4)
print("method 1: for G2: theta = ", Ex4_method1)
print("method 1: for G3: theta = ", 2*math.pi - abs(Ex4_method1)) 

# Ex4_method2 = method2_theta(I_ex4, J_ex4, x2_ex4, y2_ex4)
# print("method 2: for G2: theta_acute = ", Ex4_method2)
# print("method 2: for G2: theta_central = ",math.pi + Ex4_method2)

print("\n\r**note: \r\twhen beta > alpha, method 1 finds the angle between the intersecting lines (not neccessarilty the acute angle")
print("\r\tmethod 2 always finds the acute angle")

print("**note: for method 1: G3:  if theta is positive, theta = 2pi - theta")

##### Example 4b: 
print("\n\rEXAMPLE 4b: switching start and finishing points ")
I_ex4b = I_ex4 - x2_ex4
J_ex4b = J_ex4 - y2_ex4

x2_ex4b = -x2_ex4
y2_ex4b = -y2_ex4
Ex4b_method1 = method1_theta(I_ex4b, J_ex4b, x2_ex4b, y2_ex4b)
print("method 1: for G2: theta = ", Ex4b_method1)
print("method 1: for G2: theta_central = ", 2*math.pi + Ex4b_method1)
print("method 1: for G3: theta = ", abs(Ex4b_method1)) 


# Ex4b_method2 = method2_theta(I_ex4b, J_ex4b, x2_ex4b, y2_ex4b)
# print("method 1: for G2: theta_acute = ", Ex4b_method2)
# print("method 1: for G2: theta_central = ", (2*math.pi - math.pi) + Ex4b_method2)

print("**note: for method 1: G2:  if theta is negative, add 2pi\nG3: take absolute value of theta")

##### Example 5: 
print("\n\rEXAMPLE 5: semi circle")

I_ex5 = -5
J_ex5 = 0

x2_ex5 = -10
y2_ex5 = 0

Ex5_method1 = method1_theta(I_ex5, J_ex5, x2_ex5, y2_ex5)
print("method 1: for G2: theta = ", Ex5_method1)
print("method 1: for G3: theta = ", 2*math.pi - abs(Ex5_method1)) 

# Ex5_method2 = method2_theta(I_ex5, J_ex5, x2_ex5, y2_ex5)
# print("method 1: for G2: theta = ", Ex5_method2)
# print("method 1: for G2: theta_central = ", (2*math.pi - math.pi) + Ex5_method2)


##### Example 6: 
print("\n\rEXAMPLE 6: quarter circle")

I_ex6 = -5
J_ex6 = 0

x2_ex6 = -5
y2_ex6 = 5

Ex6_method1 = method1_theta(I_ex6,  J_ex6, x2_ex6, y2_ex6)
print("method 1: for G2: theta = ", Ex6_method1)
print("method 1: for G3: theta = ", 2*math.pi - abs(Ex6_method1)) 

# Ex6_method2 = method2_theta(I_ex6,  J_ex6, x2_ex6, y2_ex6)
print('**note: method 2 results in division by zero for quarter circles....')
# print("method 1: for G2: theta = ", Ex6_method2)
# print("method 1: for G2: theta_central = ", (2*math.pi - math.pi) + Ex5_method2)


##### Example 7: 
print("\n\rEXAMPLE 7: Full circle")
I_ex7 = -5
J_ex7 = 0

x2_ex7 = 0 
y2_ex7 = 0
Ex7_method1 = method1_theta(I_ex7,  J_ex7, x2_ex7, y2_ex7)
print("method 1: for G2: theta = ", Ex7_method1)
print("method 1: for G2: theta = ", 2*math.pi - abs(Ex7_method1))

print("**note:for method 1: if theta = 0, add 2pi because it is a full circle")

### note in above sections I accidently switched G2 and G3. I fixed them for the conclusions below
print("**\n\rsome conclusions:")
print("1) use Method 1")
print("2) for G3 moves: if theta <= 0 add 2pi (or 360 degrees)")
print("3) for G2 moves: if theta < 0, take absolute value of theta")
print("4) for G2 moves: if theta >=0, theta = 2pi - abs(theta) ")





 
 





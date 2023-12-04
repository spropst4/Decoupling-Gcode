'''
Good tutorials:
https://towardsdatascience.com/making-publication-quality-figures-in-python-part-ii-line-plot-legends-colors-4430a5891706
'''
import numpy as np
# load packages
import matplotlib as mpl
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator,FormatStrFormatter,MaxNLocator
import matplotlib.cm as cm
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.colors as mcol
#import proplot as pplt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

## round to nearest interval
def round_to_multiple(n, multiple):
    result = multiple * round(n/multiple)
    if result <= round(n):
        result += multiple/2
    return result

# set default global settings
mpl.rcParams['pdf.fonttype'] = 42
mpl.rcParams['ps.fonttype'] = 42
mpl.rcParams['font.family'] = 'Arial'

SMALL_SIZE = 8
MEDIUM_SIZE = 10
BIGGER_SIZE = 12

mpl.rc('font', size=SMALL_SIZE)          # controls default text sizes
mpl.rc('axes', titlesize=SMALL_SIZE)     # fontsize of the axes title
mpl.rc('axes', labelsize=MEDIUM_SIZE)    # fontsize of the x and y labels
mpl.rc('xtick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('ytick', labelsize=SMALL_SIZE)    # fontsize of the tick labels
mpl.rc('legend', fontsize=SMALL_SIZE)    # legend fontsize
mpl.rc('figure', titlesize=BIGGER_SIZE)  # fontsize of the figure title

# Functions
def accel_time_linear(v_0, v_f, accel):
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

def accel_time_S_curve(v_0, jerk_ratio, velocity_input, accel_input):
    '''
    https://math.stackexchange.com/questions/2232105/question-about-s-curve-acceleration-and-deceleration-control
    http://www.et.byu.edu/~ered/ME537/Notes/Ch5.pdf
    '''

    from sympy import symbols, solve

    t_accel = symbols('t_accel')

    # v_m = v_0 + 0.5*jerk_ratio*t**2 # from zero to mid accel
    # v_max = v_0 - J*t_m**2 + 2*J*t_m*t - 0.5*J*t**2 # from mid to max

    # solve for t_m
    t = t_accel
    accel_max = accel_input/(1 - (jerk_ratio * 0.5))
    J =  2 * accel_max/(t_accel * jerk_ratio)
    v2 = velocity_input - accel_max**2/(2*J)

    find_t_accel = v2 + accel_max*t - J*t**2/2

    t_accel = solve(find_t_accel)[0]

    return float(t_accel)

def accel_time_Half_Sine(velocity_input, accel_input):
    '''
    https://math.stackexchange.com/questions/2232105/question-about-s-curve-acceleration-and-deceleration-control
    http://www.et.byu.edu/~ered/ME537/Notes/Ch5.pdf
    '''

    from sympy import symbols, solve
    import numpy as np
    t_accel = symbols('t_accel')
    accel_max = accel_input/0.637
    P = 2*t_accel
    B = 2*np.pi/P
    t = t_accel
    find_t_accel = -accel_max/B *np.cos(np.pi) + accel_max/B - velocity_input #-accel_max/B *(np.cos(B*t)) - velocity_input
    t_accel = solve(find_t_accel)[0]
    return float(t_accel)

def velocity_linear(t_total, t_accel, accel_input, velocity_input):
    time_range = list(np.linspace(0, t_total, num = 1000))
    vel_list = []
    for i in range(len(time_range)):
        t_current = time_range[i]
        if 0 <= t_current < t_accel:
            v_current = accel_input*t_current
            vel_list.append(v_current)

        elif t_accel <= t_current < t_total - t_accel:
            v_current = velocity_input
            vel_list.append(v_current)

        else:
            t_current_calc = t_current - (t_total - t_accel)
            v_current = velocity_input - accel_input*t_current_calc
            vel_list.append(v_current)
    return time_range, vel_list

def velocity_halfSine(t_total, t_accel, accel_input, velocity_input):
    '''
      avg value of half sine: https://www.electronics-tutorials.ws/accircuits/average-voltage.html
      accel_input = 0.637*accel_max

      A = accel =  A*sin(B(x + C)) + D
      A = Amplitude
      B = 2pi/period
      C = Phase shift left
      D = vertical shift

      v(t) = Integral(accel) = -A cos(Bx)/B + Constant

      '''

    time_range = list(np.linspace(0, t_total, num=1000))
    a_max = accel_input / 0.637
    Period = 2 * t_accel
    B = 2 * np.pi / Period

    vel_list = []
    for i in range(len(time_range)):
        t_current = time_range[i]

        if 0 <= t_current < t_accel:
            v_current = velocity_input/2 - a_max/B * np.cos(B*t_current)
            vel_list.append(v_current)

        elif t_accel <= t_current < t_total - t_accel:
            v_current = velocity_input
            vel_list.append(v_current)

        else:
            t_current_calc = t_current - (t_total - t_accel)
            v_current = velocity_input/2 + a_max / B * np.cos(B * t_current_calc)
            vel_list.append(v_current)

    print(vel_list)
    return time_range, vel_list

# Create Data
velocity_input = 25

accel_input = 1000
t_total = 0.1
jerk_ratio = 2/3

t_accel_linear = accel_time_linear(0, velocity_input, accel_input)[1]
t_accel_halfSine = accel_time_Half_Sine(velocity_input, accel_input)
t_accel_Scurve = accel_time_S_curve(0, jerk_ratio, velocity_input, accel_input)


vel_LinearResult = velocity_linear(t_total, t_accel_linear, accel_input, velocity_input)
vel_HalfSineResult = velocity_halfSine(t_total, t_accel_halfSine, accel_input, velocity_input)



# plt.plot(vel_LinearResult[0], vel_LinearResult[1])
plt.plot(vel_HalfSineResult[0], vel_HalfSineResult[1])
plt.show()


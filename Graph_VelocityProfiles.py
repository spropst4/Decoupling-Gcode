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


def accel_linear(accel_input, t_total, t_accel):
    time_range = list(np.linspace(0, t_total, num = 1000))

    accel_list = [0]
    t_list_total = [0]

    for i in range(len(time_range)):
        t_current = time_range[i]

        if 0 <= t_current < t_accel:
            accel_current = accel_input

        elif t_accel <= t_current < t_total-t_accel:
            accel_current = 0

        else:
            accel_current = -accel_input

        accel_list.append(accel_current)
        t_list_total.append(t_current)

    accel_list.append(0)
    t_list_total.append(t_total)

    return t_list_total, accel_list

def accel_halfSine(accel_input, t_total, t_accel):
    '''
    avg value of half sine: https://www.electronics-tutorials.ws/accircuits/average-voltage.html
    accel_input = 0.637*accel_max

    y = A*sin(B(x + C)) + D
    A = Amplitude
    B = 2pi/period
    C = Phase shift left
    D = vertical shift

    '''
    time_range = list(np.linspace(0, t_total, num=1000))

    t_list_total = []
    accel = []
    accel_max = accel_input / 0.637

    period = 2*t_accel
    B_const = (2*np.pi)/period

    for i in range(len(time_range)):
        t_current = time_range[i]
        if 0 <= t_current < t_accel:
            accel_current = accel_max*np.sin(B_const*t_current)
            if round(accel_current) == 0:
                accel_current = 0


        elif t_accel <= t_current < t_total-t_accel:
            accel_current = 0


        else:
            t_current_calc = t_current - (t_total - t_accel)
            accel_current = -accel_max * np.sin(B_const*t_current_calc)
            if round(accel_current) == 0:
                accel_current = 0

        accel.append(accel_current)
        t_list_total.append(t_current)

    return t_list_total, accel

def accel_S_curve(accel_input, t_total, t_accel, jerk_ratio):
    '''
    jerk ratio: https://product-help.schneider-electric.com/Machine%20Expert/V1.1/en/m241pto/m241pto/M241Lib-PTO-Configuration/M241Lib-PTO-Configuration-5.htm
    e.g., JerkRatio 66%: 2/3 of the acceleration and deceleration time is spent in increasing and decreasing the acceleration and deceleration value.

    Peak acceleration equations: https://docs.roboticsys.com/rmp/topics/motion/motion-concepts/s-curve-motion-profiles-command-acceleration-vs.-peak-acceleration

    More on S-curves: http://www.et.byu.edu/~ered/ME537/Notes/Ch5.pdf

    '''
    time_range = list(np.linspace(0, t_total, num=1000))
    t_list_total = []
    accel_list = []
    accel_max = accel_input/(1 - (jerk_ratio * 0.5))

    t_accel = t_accel
    t_accel_ratio = (t_accel * jerk_ratio) / 2 # time to do the increasing/decr portion

    for i in range(len(time_range)):
        t_current = time_range[i]

        # acceleration (+)
        if 0 <= t_current < t_accel:
            if 0 <= t_current < t_accel_ratio:
                if jerk_ratio != 0:
                    accel_current = (accel_max / t_accel_ratio) * t_current
                else:
                    accel_current = accel_max

            elif t_accel_ratio <= t_current < t_accel - t_accel_ratio:
                accel_current = accel_max

            else:
                t_current_calc = t_current - (t_accel - t_accel_ratio)
                if jerk_ratio != 0:
                    accel_current = -(accel_max / t_accel_ratio) * t_current_calc + accel_max
                else:
                    accel_current = 0

        # acceleration = 0
        elif t_accel <= t_current < t_total - t_accel:
            accel_current = 0

        # deceleration
        else:
            if t_total - t_accel <= t_current <  (t_total - t_accel) + t_accel_ratio:
                t_current_calc = t_current - (t_total - t_accel)
                if jerk_ratio != 0:
                    accel_current = -(accel_max / t_accel_ratio) * t_current_calc
                else:
                    accel_current = -accel_max

            elif (t_total - t_accel) + t_accel_ratio <= t_current < t_total - t_accel_ratio:
                accel_current = -accel_max

            else:
                t_current_calc = t_current - (t_total - t_accel_ratio)
                if jerk_ratio != 0:
                    accel_current = (accel_max / t_accel_ratio) * t_current_calc - accel_max
                else:
                    accel_current = 0
        accel_list.append(accel_current)
        t_list_total.append(t_current)

    return t_list_total, accel_list

def velocity(time_data, accel_data):
    import numpy as np
    import scipy
    from scipy.integrate import simpson
    from numpy import trapz

    vel_current = 0
    vel_list = []
    time_list = []
    incr = 2
    for i in range(len(accel_data)-incr):
        start = i
        end = i + incr
        vel_current += trapz(accel_data[start:end], x = time_data[start:end], dx = incr)
        #vel_current +=simpson(accel_data[start:end], dx = incr)
        vel_list.append(vel_current)
        time_current = time_data[end]
        time_list.append(time_current)

    return time_list, vel_list


# Create Data
velocity_input = 20
accel_input = 1000
t_total = 0.1
jerk_ratio = 2/3

t_accel_linear = float(accel_time_linear(0, velocity_input, accel_input)[1])
t_accel_halfSine = accel_time_Half_Sine(velocity_input, accel_input)
t_accel_Scurve = accel_time_S_curve(0, jerk_ratio, velocity_input, accel_input)  #t_accel_linear

print(t_accel_linear, t_accel_halfSine, t_accel_Scurve)

accel_linearResult = accel_linear(accel_input, t_total, t_accel_linear)
accel_halfSineResult = accel_halfSine(accel_input, t_total, t_accel_halfSine)
accel_ScurveResult = accel_S_curve(accel_input, t_total, t_accel_Scurve, jerk_ratio)


vel_LinearResult = velocity(accel_linearResult[0], accel_linearResult[1])
vel_halfSineResult = velocity(accel_halfSineResult[0], accel_halfSineResult[1])
vel_ScurveResult = velocity(accel_ScurveResult[0], accel_ScurveResult[1])

fig_vel, (ax1_v, ax2_v, ax3_v) = plt.subplots(1,3)
ax1_v.plot(accel_linearResult[0], accel_linearResult[1])
ax2_v.plot(accel_halfSineResult[0], accel_halfSineResult[1])
ax3_v.plot(accel_ScurveResult[0], accel_ScurveResult[1])

plt.setp((ax1_v, ax2_v, ax3_v),
         xlim=(-t_total/10,t_total+ t_total/10),
         ylim=(-accel_input - 1000, accel_input + 1000)
         )

# plt.plot(accel_linearResult[0], accel_linearResult[1])
# plt.plot(accel_halfSineResult[0], accel_halfSineResult[1])
# plt.plot(accel_ScurveResult[0], accel_ScurveResult[1])

fig_accel, (ax1_a, ax2_a, ax3_a) = plt.subplots(1, 3)
ax1_a.plot(vel_LinearResult[0], vel_LinearResult[1])
ax2_a.plot(vel_halfSineResult[0], vel_halfSineResult[1])
ax3_a.plot(vel_ScurveResult[0], vel_ScurveResult[1])

# plt.plot(vel_LinearResult[0], vel_LinearResult[1])
# plt.plot(vel_halfSineResult[0], vel_halfSineResult[1])
# plt.plot(vel_ScurveResult[0], vel_ScurveResult[1])
plt.setp((ax1_a, ax2_a, ax3_a)
         #xlim=(0,t_total),
         #ylim=(0, velocity_input + 2)
         )


# fig_all, (ax2, ax1) = plt.subplots(2,1)
# x_hsine = []
# for i in range(len(accel_halfSineResult[0])):
#     x_current = accel_halfSineResult[0][i] + t_total + 2
#     x_hsine.append(x_current)
#
# x_scurve = []
# for i in range(len(accel_ScurveResult[0])):
#     x_current = accel_ScurveResult[0][i] + max(x_hsine) +2
#     x_scurve.append(x_current)
#
# ax1.axhline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
# ax1.axvline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
# ax1.plot(accel_linearResult[0], accel_linearResult[1])
# ax1.plot(x_hsine, accel_halfSineResult[1])
# ax1.plot(x_scurve, accel_ScurveResult[1])
#
# x_hsine = []
# for i in range(len(vel_halfSineResult[0])):
#     x_current = vel_halfSineResult[0][i] + t_total + 2
#     x_hsine.append(x_current)
#
# x_scurve = []
# for i in range(len(vel_halfSineResult[0])):
#     x_current = vel_halfSineResult[0][i] + max(x_hsine) + 2
#     x_scurve.append(x_current)
#
# ax2.axvline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
# ax2.plot(vel_LinearResult[0], vel_LinearResult[1])
# ax2.plot(x_hsine, vel_halfSineResult[1])
# ax2.plot(x_scurve, vel_ScurveResult[1])
#
#
# ax1.tick_params(axis ='both',
#                 bottom = False,
#                 direction ='in',
#                 labelbottom = False,
#                 labelleft = False)
#
# ax2.tick_params(axis ='both',
#                 bottom = False,
#                 direction ='in',
#                 labelbottom = False,
#                 labelleft = False)
#
# plt.setp(ax2,
#          xlim=(0,max(x_scurve)+2),
#          ylim=(0, velocity_input + 2)
#          )



plt.show()


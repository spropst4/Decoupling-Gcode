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
def accel_length(v_0, v_f, accel):
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

def accel_linear(accel_input, t_total, t_accel):
    accel_list = [0]
    t_list_total = [0]

    t_list_pos = list(np.linspace(0, t_accel, num=100))
    for t in t_list_pos:
        accel_current = accel_input
        accel_list.append(accel_current)
        t_list_total.append(t)

    t_zero_i = t_accel
    t_zero_f = t_accel + (t_total - t_accel*2)
    t_list_0 = list(np.linspace(t_zero_i, t_zero_f, num=100))
    for t in t_list_0:
        accel_current = 0
        accel_list.append(accel_current)
        t_list_total.append(t)

    t_list_neg = list(np.linspace(t_zero_f, t_zero_f+t_accel, num = 100))
    for t in t_list_neg:
        accel_current = -accel_input
        accel_list.append(accel_current)
        t_list_total.append(t)

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
    t_list_total = []
    accel = []
    accel_max = accel_input / 0.637

    period = 2*t_accel
    B_const = (2*np.pi)/period
    print(B_const)

    t_pos_f = t_accel
    t_list_pos = list(np.linspace(0, t_pos_f, num = 100))
    for t in t_list_pos:
        accel_current = accel_max*np.sin(B_const*t)
        if round(accel_current)== 0:
            accel_current = 0
        accel.append(accel_current)
        t_list_total.append(t)

    t_zero_f = t_pos_f + (t_total - 2 * t_pos_f)
    t_list_0 = list(np.linspace(t_pos_f, t_zero_f, num = 100))
    for t in t_list_0:
        accel_current = 0
        accel.append(accel_current)
        t_list_total.append(t)

    t_list_neg = list(np.linspace(t_zero_f, t_total, num = 100))
    for t in t_list_neg:
        t_calc = t - t_zero_f
        accel_current = -accel_max * np.sin(B_const*t_calc)
        if round(accel_current) == 0:
            accel_current = 0
        accel.append(accel_current)
        t_list_total.append(t)

    return t_list_total, accel

def accel_S_curve(accel_input, t_total, t_accel, jerk_ratio):
    '''
    jerk ratio: https://product-help.schneider-electric.com/Machine%20Expert/V1.1/en/m241pto/m241pto/M241Lib-PTO-Configuration/M241Lib-PTO-Configuration-5.htm
    Peak acceleration equations: https://docs.roboticsys.com/rmp/topics/motion/motion-concepts/s-curve-motion-profiles-command-acceleration-vs.-peak-acceleration
    '''
    t_list_total = []
    accel_list = []
    accel_max = accel_input/(1 - (jerk_ratio * 0.5))

    t_accel_half = (t_accel * jerk_ratio) / 2 # time to do the increasing/decr portion

    # positive acceleration
    t_neg_incr_f = t_accel_half
    t_list_neg_dec = np.linspace(0, t_neg_incr_f, num = 33)
    for t in t_list_neg_dec:
        if jerk_ratio != 0:
            accel_current = (accel_max / t_accel_half) * t
        else:
            accel_current = accel_max

        accel_list.append(accel_current)
        t_list_total.append(t)

    t_const_pos_i = t_neg_incr_f
    t_const_pos_f = t_const_pos_i + (t_accel - 2 * t_accel_half)
    t_list_const_pos = np.linspace(t_const_pos_i, t_const_pos_f, num=34)
    for t in t_list_const_pos:
        accel_current = accel_max
        accel_list.append(accel_current)
        t_list_total.append(t)

    t_pos_dec_i = t_const_pos_f
    t_neg_incr_f = t_pos_dec_i + t_accel_half
    t_list_pos_dec = np.linspace(t_pos_dec_i, t_neg_incr_f, num=33)
    for t in t_list_pos_dec:
        t_calc = t - t_pos_dec_i
        if jerk_ratio != 0:
            accel_current = -(accel_max / t_accel_half) * t_calc + accel_max
        else:
            accel_current = 0
        accel_list.append(accel_current)
        t_list_total.append(t)

    # acceleration = 0
    t_zero_i = t_accel
    t_zero_f = t_zero_i + (t_total - 2 * t_accel)
    t_list_const_pos = np.linspace(t_zero_i, t_zero_f, num=100)
    for t in t_list_const_pos:
        accel_current = 0
        accel_list.append(accel_current)
        t_list_total.append(t)

    # neg acceleration
    t_neg_dec_i = t_zero_f
    t_neg_dec_f = t_neg_dec_i + t_accel_half
    t_list_neg_dec = np.linspace(t_neg_dec_i, t_neg_dec_f, num=33)
    for t in t_list_neg_dec:
        t_calc = t - t_neg_dec_i
        if jerk_ratio != 0:
            accel_current = -(accel_max / t_accel_half) * t_calc
        else:
            accel_current = -accel_max

        accel_list.append(accel_current)
        t_list_total.append(t)

    t_const_neg_i = t_neg_dec_f
    t_const_neg_f = t_const_neg_i + (t_accel - 2 * t_accel_half)
    t_list_const_pos = np.linspace(t_const_neg_i, t_const_neg_f, num=34)
    for t in t_list_const_pos:
        accel_current = -accel_max
        accel_list.append(accel_current)
        t_list_total.append(t)

    t_neg_incr_i = t_const_neg_f
    t_neg_incr_f = t_neg_incr_i + t_accel_half
    t_list_pos_dec = np.linspace(t_neg_incr_i, t_neg_incr_f, num=33)
    for t in t_list_pos_dec:
        t_calc = t - t_neg_incr_i
        if jerk_ratio != 0:
            accel_current = (accel_max / t_accel_half) * t_calc - accel_max
        else:
            accel_current = 0
        accel_list.append(accel_current)
        t_list_total.append(t)

    return t_list_total, accel_list

def velocity(t_total, accel_data, velocity_input):
    import numpy as np
    import scipy
    from scipy.integrate import simpson
    from scipy.integrate import quad
    from numpy import trapz

    vel_current = 0
    vel_list = []
    time_list = []
    incr = 2

    for i in range(len(accel_data)-incr):
        start = i
        end = i + incr
        #vel_current += trapz(accel_data[start:end], dx = incr)
        vel_current +=simpson(accel_data[start:end], dx = incr)
        vel_list.append(vel_current/10000)

        time_current = end
        const_norm = (t_total/(len(accel_data)-1))
        time_current_norm = time_current*const_norm
        time_list.append(time_current_norm)

    v_max = max(vel_list)
    vel_const = velocity_input/v_max

    if v_max != velocity_input:
        for i in range(len(vel_list)):
            vel_list[i] = vel_list[i]*vel_const

    return time_list, vel_list

# Create Data
velocity_input = 20

accel_input = 1000
t_total = 5
t_accel_linear = 2 #float(accel_length(0, velocity_input, accel_input)[1])
t_accel_halfSine = t_accel_linear
t_accel_Scurve = t_accel_linear
jerk_ratio = 0.5

accel_linearResult = accel_linear(accel_input, t_total, t_accel_linear)
accel_halfSineResult = accel_halfSine(accel_input, t_total, t_accel_halfSine)
accel_ScurveResult = accel_S_curve(accel_input, t_total, t_accel_Scurve, jerk_ratio)

# print(len(accel_linearResult[0]))

vel_LinearResult = velocity(t_total, accel_linearResult[1], velocity_input)
vel_halfSineResult = velocity(t_total, accel_halfSineResult[1], velocity_input)
vel_ScurveResult = velocity(t_total, accel_ScurveResult[1], velocity_input)



fig_vel, (ax1_v, ax2_v, ax3_v) = plt.subplots(1,3)
ax1_v.plot(accel_linearResult[0], accel_linearResult[1])
ax2_v.plot(accel_halfSineResult[0], accel_halfSineResult[1])
ax3_v.plot(accel_ScurveResult[0], accel_ScurveResult[1])

plt.setp((ax1_v, ax2_v, ax3_v),
         xlim=(-1,t_total+1),
         #ylim=(0, accel_input + 2),
         xticklabels  = [],
         yticklabels = []
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
plt.setp((ax1_a, ax2_a, ax3_a),
         xlim=(0,t_total),
         ylim=(0, velocity_input + 2)
         )



fig_all, (ax2, ax1) = plt.subplots(2,1)
x_hsine = []
for i in range(len(accel_halfSineResult[0])):
    x_current = accel_halfSineResult[0][i] + t_total + 2
    x_hsine.append(x_current)

x_scurve = []
for i in range(len(accel_ScurveResult[0])):
    x_current = accel_ScurveResult[0][i] + max(x_hsine) +2
    x_scurve.append(x_current)

ax1.axhline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
ax1.axvline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
ax1.plot(accel_linearResult[0], accel_linearResult[1])
ax1.plot(x_hsine, accel_halfSineResult[1])
ax1.plot(x_scurve, accel_ScurveResult[1])

x_hsine = []
for i in range(len(vel_halfSineResult[0])):
    x_current = vel_halfSineResult[0][i] + t_total + 2
    x_hsine.append(x_current)

x_scurve = []
for i in range(len(vel_halfSineResult[0])):
    x_current = vel_halfSineResult[0][i] + max(x_hsine) + 2
    x_scurve.append(x_current)

ax2.axvline(0, color = 'gray', alpha = 0.3, linewidth = 0.5)
ax2.plot(vel_LinearResult[0], vel_LinearResult[1])
ax2.plot(x_hsine, vel_halfSineResult[1])
ax2.plot(x_scurve, vel_ScurveResult[1])


ax1.tick_params(axis ='both',
                bottom = False,
                direction ='in',
                labelbottom = False,
                labelleft = False)

ax2.tick_params(axis ='both',
                bottom = False,
                direction ='in',
                labelbottom = False,
                labelleft = False)

plt.setp(ax2,
         xlim=(0,max(x_scurve)+2),
         ylim=(0, velocity_input + 2)
         )

plt.show()


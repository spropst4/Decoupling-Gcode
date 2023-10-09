import numpy as np

def generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type):
    #arc_length = r*theta_between_moves
    theta_between_moves = section_arc_length/r
    num_sections = (2*np.pi*circle_fraction)/theta_between_moves
    num_sections = round(num_sections)
    theta_between_moves = (2*np.pi*circle_fraction)/num_sections


    print('updated to section arc length so that num_sections is a whole number: ', (r*theta_between_moves))

    #theta_between_moves = (np.pi / (circle_fraction/2)) / num_sections


    if start_settings[0] == 'initial':
        sign = 1
        x_prev = r
        y_prev = 0
        theta_for_ij = 0
        theta_for_xy = theta_between_moves

    if start_settings[0] == 'update' and pattern_type == 'spiral':
        x_output = start_settings[1]
        if x_output < 0:
            sign = -1
        else:
            sign = 1
        x_prev = r
        y_prev = 0
        theta_for_ij = 0
        theta_for_xy = theta_between_moves

    elif start_settings[0] == 'update' and pattern_type == 'not spiral':
        x_prev = start_settings[2]
        y_prev = start_settings[3]
        theta_for_xy = start_settings[4]
        theta_for_ij = start_settings[5]
        sign = 1

    for c in range(num_sections):
        x = round(r*np.cos(theta_for_xy), 10)
        y = round(r * np.sin(theta_for_xy),10)

        x_rel = x - x_prev
        y_rel = y - y_prev

        x_prev = x
        y_prev = y

        i = round(-r*np.cos(theta_for_ij),10)
        j = round(-r*np.sin(theta_for_ij),10)

        theta_for_ij += theta_between_moves
        theta_for_xy += theta_between_moves


        print('\n\rG3 X'+ str(sign*x_rel) + ' Y' + str(sign*y_rel) + ' I' + str(sign*i) + ' J'+ str(sign*j))


    return ['update', sign*x_rel, x_prev, y_prev, theta_for_xy, theta_for_ij]



# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    r = 2
    section_arc_length = 0.25
    circle_fraction = 1/2
    start_settings = ['initial']

    '''
    spiral pattern
    - pattern_type = 'spiral'
    - can do increasing and decreasing spirals
    '''
    pattern_type = 'spiral'  # options: 'spiral', 'not spiral'
    start_settings = generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type)
    while r>= 20:
        section_arc_length += 0.5
        print('---', start_settings)
        r -= 2
        start_settings = generateCircleG3(r, section_arc_length, circle_fraction, start_settings, pattern_type)

    '''
    full circle from circle fractions
    - consecutive loops must use some section arc length
    - pattern_type = 'not spiral'    
    '''
    # pattern_type = 'not spiral'  # options: 'spiral', 'not spiral'
    # start_settings = generateCircle(r, section_arc_length, circle_fraction, start_settings, pattern_type)
    # circle_fraction_total = circle_fraction
    # while circle_fraction_total < 1:
    #     start_settings = generateCircle(r, section_arc_length, circle_fraction, start_settings, pattern_type)
    #     circle_fraction_total += circle_fraction


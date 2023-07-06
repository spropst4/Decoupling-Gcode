import numpy as np
def generateCircle(num_sections_per_quarter, r_start, r_final, filament_width, export_gcode_txt, setpress, toggle_ON, toggle_OFF):
    color_flag_ON = 1
    with open(export_gcode_txt, 'w') as f:
        f.write('\n\rG91')

        for elem in setpress:
            f.write(elem)


        theta_between_moves = (np.pi / 2) / num_sections_per_quarter
        r = r_start
        color_start = toggle_ON[0]
        color_flag_ON = 0

        f.write(color_start)
        while r <= r_final:
            theta_for_ij = 0
            theta_for_xy = theta_between_moves

            x_prev = r
            y_prev = 0

            for i in range(num_sections_per_quarter*4):
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

                f.write('\n\rG3 X'+ str(x_rel) + ' Y' + str(y_rel) + 'I' + str(i) +  ' J'+ str(j))
                if color_flag_ON == 0: # odd segments
                    f.write(toggle_ON[1])
                    f.write(toggle_OFF[0])
                    color_flag_ON = 1
                else:
                    f.write(toggle_ON[0])
                    f.write(toggle_OFF[1])
                    color_flag_ON = 0






            r += filament_width
            f.write('\n\rG1 X'+ str(filament_width))

        if color_flag_ON == 0:  # odd segments
            f.write(toggle_OFF[0])
        else:
            f.write(toggle_OFF[1])


export_gcode_txt = '1DGC_GenerateCircle_divided.txt'
num_sections_per_quarter = 5

r_start = 2
r_final = 15

filament_width = 1

set_press1 = '\n\rsetpress1'
set_press2 = '\n\rsetpress2'

toggleON_1 = '\n\rtoggle on 1'
toggleON_2 = '\n\rtoggle on 2'

toggleOFF_1 = '\n\rtoggle off 1'
toggleOFF_2 = '\n\rtoggle off 2'

setpress = [set_press1, set_press2]
toggle_ON = [toggleON_1, toggleON_2]
toggle_OFF = [toggleOFF_1, toggleOFF_2]

generateCircle(num_sections_per_quarter, r_start, r_final, filament_width, export_gcode_txt,setpress, toggle_ON, toggle_OFF)



import numpy as np

def find_distances(myline, ch1, ch2, hex_side_length, direction, offset):
    if ch1 in myline or ch2 in myline:
        list = myline.split(" ")
        distance1 = 0
        distance2 = 0
        offset_list = []
        for elem in list:

            if ch1 in elem :
                distance1 = elem.strip(ch1)
                distance1 = float(distance1) / float(5)
                distance1 = direction * distance1 * hex_side_length

            if ch2 in elem:
                distance2 = elem.strip(ch2)
                distance2 = float(distance2) / float(5)
                distance2 = direction * distance2 * hex_side_length

            if '{offset}' in elem or '{offset_x}' in elem or '{offset_y}' in elem:
                offset_update = float(elem.replace('{offset}', str(offset)).replace('{offset_x}', str(offset/np.sqrt(5))).replace('{offset_y}', str(offset*2/np.sqrt(5))))
                offset_list.append(direction * offset_update)

            else:
                offset_list.append(0)

        while len(offset_list) < 5:
            offset_list.append(0)

        offset1 = offset_list[2]
        offset2 = offset_list[4]
        return list[0] + ' ' + ch1 + str(distance1 + offset1) + ' ' + ch2 + str(distance2 + offset2)

    else:
        return myline

def open_and_edit_gcode(gcode_txt, toggle_ON_list, toggle_OFF_list, hex_side_length, offset, filament_width, visualize):
    gcode_list = []
    gcode_list_reverse = []
    with open(gcode_txt, "r") as gcode:
        for myline in gcode:  # For each elem in the file,
            myline = myline.strip('\n')
            #myline = myline.replace('G0', 'G1')
            #myline = myline.removeprefix('G1 ').removeprefix('G0 ')
            myline = myline.replace("'Material 1 ON", toggle_ON_list[0]).replace("'Material 2 ON", toggle_ON_list[1]).replace("'Material 1 OFF", toggle_OFF_list[0]).replace("'Material 2 OFF", toggle_OFF_list[1])
            update_xy_distances = find_distances(myline, 'X', 'Y', hex_side_length, 1, offset)
            reverse_xy_direction = find_distances(myline, 'X', 'Y', hex_side_length, -1, offset)

            myline = update_xy_distances
            myline_reverse = reverse_xy_direction

            if visualize == False:
                myline = myline.replace('G0', 'G1')
                myline_reverse = myline_reverse.replace('G0', 'G1')



            myline = myline.replace('{gap}', 'G1 Y'+str(filament_width/2))
            myline_reverse = myline_reverse.replace('{gap}', 'G1 Y-' + str(filament_width / 2))

            gcode_list.append(myline)
            gcode_list_reverse.append(myline_reverse)


        gcode_list = [x for x in gcode_list if x != ""] # removes spaces
        gcode_list_reverse = [x for x in gcode_list_reverse if x != ""]  # removes spaces



        gcode.close()
        return gcode_list, gcode_list_reverse



gcode_txt_1RepeatUnit = 'Triangle_lattice_honeycomb_1RepeatUnit_Offset_gap.txt'
gcode_txt_Section1_Only = 'Triangle_lattice_honeycomb_Section1_Only_Offset.txt'
visualize = True

hex_side_length = 10
number_of_repeat_units = 3
num_layers = 1
layer_height = 1
filament_width = 1

offset = 3

toggle_ON_1 = 'Material 1 ON'
toggle_OFF_1 = 'Material 1 OFF'

toggle_ON_2 = 'Material 2 ON'
toggle_OFF_2 = 'Material 2 OFF'

toggle_ON_list = [toggle_ON_1, toggle_ON_2]
toggle_OFF_list = [toggle_OFF_1, toggle_OFF_2]


gcode_list_1repeat_unit = open_and_edit_gcode(gcode_txt_1RepeatUnit, toggle_ON_list, toggle_OFF_list, hex_side_length,
                                              offset, filament_width, visualize)
odd_layers_1repeat_unit = gcode_list_1repeat_unit[0]
even_layers_1repeat_unit = gcode_list_1repeat_unit[1]

gcode_list_Section1_Only = open_and_edit_gcode(gcode_txt_Section1_Only, toggle_ON_list, toggle_OFF_list,
                                               hex_side_length, offset, filament_width, visualize)
odd_layers_Section1_Only = gcode_list_Section1_Only[0]
even_layers_Section1_Only = gcode_list_Section1_Only[1]



print('G91')
print(toggle_ON_1)
print('G1 X' + str(offset))
for layer in range(num_layers):
    print("'layer " + str(layer+1))

    if (layer + 1)%2 != 0:
        for repeat in range(number_of_repeat_units):
            for elem in odd_layers_1repeat_unit:
                print(elem)

        for elem in odd_layers_Section1_Only:
            print(elem)

    else:
        for repeat in range(number_of_repeat_units):
            for elem in even_layers_1repeat_unit:
                print(elem)
        for elem in even_layers_Section1_Only:
            print(elem)

    print('G1 Z' + str(layer_height))

print(toggle_OFF_1)





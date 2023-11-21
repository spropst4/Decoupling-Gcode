def GenerateSpiral(r_start, r_end, repeat):
    sign = -1
    distance_count = 0
    r = r_start
    d = r * 2
    fraction =0.5
    for i in range(repeat):
        while r < r_end:
            f.write('\nG3 X'+str(sign*d) + ' Y0' + ' I' +str(sign*r) + ' J0')
            distance_count += sign*d
            r += r*fraction
            d = r*2
            sign = sign * -1
        distance_x = -distance_count

        distance_x = distance_x-1.5*r_start

        if i+1 != repeat:
            f.write('\nG1 Z' + str(2))
            f.write('\nG1 X' + str(distance_x))
            f.write('\nG1 Z' + str(-2))
        else:
            f.write('\nG3 X'+str(sign*d) + ' Y0' + ' I' +str(sign*r) + ' J0')

        r = r_start
        d = r * 2
        sign = 1
        distance_count = 0

export_file = 'Spiral_gcode.txt'
r_start = 1
r_end = 15
r_increment = 2
repeat = 2

f = open(export_file, 'w')
f.write('\nG91')
GenerateSpiral(r_start, r_end, repeat)

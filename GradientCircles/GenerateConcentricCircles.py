def GenerateConcentricCircles(r_start, r_end):
    sign = -1
    distance_count = 0
    r = r_start
    d = r * 2
    fraction = 0.2

    while r < r_end:
        f.write('\nG3 X0 Y0' + ' I' +str(sign*r) + ' J0')
        distance_count += sign*d
        r += 1.5#r*fraction
        d = r*2
        f.write('\nG1 X0.5')

export_file = 'Circles_gcode.txt'
r_start = 5
r_end = 15

f = open(export_file, 'w')
f.write('\nG91')
GenerateConcentricCircles(r_start, r_end)

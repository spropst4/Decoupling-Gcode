def GenerateSpiral(r_start, r_increment, r_end, repeat):
    r_start = 1
    r_end = 100
    r = r_start
    d = r*2
    sign = -1
    distance_count = 0
    for i in range(repeat):
        while r <= r_end:
            print('G3 X'+str(sign*d) + ' Y0' + ' I' +str(sign*r) + ' J0')
            distance_count += sign*d
            r += r
            d = r*2
            sign = sign * -1
        distance_x = -distance_count

        if i+1 != repeat:
            print('G0 X' + str(distance_x-r_start))
        else:
            print('G3 X'+str(sign*d) + ' Y0' + ' I' +str(sign*r) + ' J0')

        r = r_start
        d = r*2
        sign = 1
        distance_count = 0

r_start = 1
r_end = 100
r_increment = 2
repeat = 2
print('G91')
GenerateSpiral(r_start, r_increment, r_end, repeat)

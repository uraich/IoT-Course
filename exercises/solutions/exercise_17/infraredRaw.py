#!/usr/bin/python3
# figure out how IR works
# These are the measured intervals

ir_data = [9065, 4516, 591, 544, 592, 545, 567, 572, 565, 592, 546, 572, 591, 546, 567, 571, 565, 572, 565, 1676, 566, 1677, 594, 1648, 595, 1648, 592, 1651, 594, 1648, 568, 1675, 568, 1695, 575, 543, 592, 1650, 566, 1676, 567, 570, 566, 1676, 592, 553, 558, 571, 566, 570, 594, 1647, 591, 547, 565, 571, 566, 1676, 591, 546, 564, 1677, 567, 1675, 567, 1676, 565, 39837, 9152, 2222, 570, 96037, 9152, 2221, 568, 96042, 9151, 2219, 569]

start = 0
tim = 0
f = open("ir_signal.dat","w")
toggle = False
f.write("%d %d\n"%(0,0))

for i in range(len(ir_data)):
    toggle = not toggle
    tim += ir_data[i]
    if toggle:
        f.write("%d %d\n"%(tim,0))
        f.write("%d %d\n"%(tim+1,1))
    else:
        f.write("%d %d\n"%(tim,1))
        f.write("%d %d\n"%(tim+1,0))
        
f.close()

ir_buffer=[]


for i in range(3,66,2):
    if ir_data[i]>800:
        ir_buffer.append(1)
        print("1",end="")
    else:
        ir_buffer.append(0)
        print("0",end="")
print("")
irValue=0x00000000
for i in range(0,4):
    for j in range(0,8):
        if ir_buffer[i*8+j]==1:
            irValue=irValue<<1
            irValue |= 0x01
        else:
            irValue=irValue<<1
            irValue &= 0xfffffffe

print("irValue: %x"%irValue)

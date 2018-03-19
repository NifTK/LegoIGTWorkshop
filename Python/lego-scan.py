#!/usr/bin/env python3
# so that script can be run from Brickman

from ev3dev.ev3 import *
import array
from time import sleep

# Connect infrared and touch sensors to any sensor ports
# and check they are connected.

ir = InfraredSensor() 
assert ir.connected, "Connect a single infrared sensor to any sensor port"

ts = TouchSensor();    assert ts.connected, "Connect a touch sensor to any port" 
# can have 2 statements on same line if use semi colon

m1 = LargeMotor('outB');    assert m1.connected, "Connect a motor to B port" 
m2 = LargeMotor('outA');    assert m2.connected, "Connect a motor to A port" 

# Put the infrared sensor into proximity mode.
ir.mode = 'IR-PROX'

# PPM header
fudge  = 10 # Padd pixes to the width, because we are calculating x from motor position
width  = 90
height = 45
maxval = 255
ppm_header = 'P6 '+str(width + fudge) + ' ' + str(height) + ' ' + str(maxval) + '\n'

# PPM image data (filled with blue)
image = array.array('B', [0, 0, 255] * ( width + fudge ) * height)

print('Motor1 Position=',m1.position)
print('Motor2 Position=',m2.position)

for y in range(0,height):
    m2.run_to_abs_pos(position_sp=y-round(height/2), speed_sp=100, stop_action="hold")
    m2.wait_while('running',timeout=500)   # Give the motor time to move
    m1.run_to_abs_pos(position_sp=-round(width/2), speed_sp=100, stop_action="hold")
    m1.wait_while('running',timeout=2000)   # Give the motor time to move
    m1.run_to_abs_pos(position_sp=round(width/2), speed_sp=40, stop_action="hold")
    
    while m1.is_running:
        x=m1.position+round(width/2)
        distance = ir.value()
        index = 3 * ((height-1-y) * ( width + fudge ) + x + round(fudge/2))
        image[index] = round(distance*255.0/100.0)           # red channel
        image[index + 1] = 0         # green channel
        image[index + 2] = 0         # blue channel
        #print(x,distance)

# Save the PPM image as a binary file
with open('depth_map.ppm', 'wb') as f:
    f.write(bytearray(ppm_header, 'ascii'))
    image.tofile(f)

Sound.beep()

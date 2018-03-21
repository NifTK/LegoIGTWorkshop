#!/usr/bin/env python3

from ev3dev.ev3 import *
import math
from time import sleep

m1 = LargeMotor('outB');    assert m1.connected, "Connect a motor to B port"
m2 = LargeMotor('outA');    assert m2.connected, "Connect a motor to A port"
m3 = MediumMotor('outC');   assert m3.connected, "Connect a motor to C port"
ir = InfraredSensor();      assert ir.connected, "Connect a infrared sensor to any port"
ts = TouchSensor();         assert ts.connected, "Connect a touch sensor to any port"

# Move home first
m1.run_to_abs_pos(position_sp=0, speed_sp=100, stop_action="hold")
m2.run_to_abs_pos(position_sp=0, speed_sp=100, stop_action="hold")
m3.run_direct(duty_cycle_sp=-30)
sleep(4)
m2.wait_while('running',timeout=1500)   # Give the motor time to move
m1.wait_while('running',timeout=1500)   # Give the motor time to move
m1.run_direct(duty_cycle_sp=0)
m2.run_direct(duty_cycle_sp=0)
m3.run_direct(duty_cycle_sp=0)

# Put the infrared sensor into proximity mode.
ir.mode = 'IR-PROX'

print('Press the touch sensor to read the motor positions')
print('WARNING! The inject motor does not seem to work, you will have to measure that manually')
print('')
print('Dst','Azm','Elv')
while True:
    while not ts.value():    # Stop program by pressing touch sensor button
        # Infrared sensor in proximity mode will measure distance to the closest
        # object in front of it.
        ir_raw = ir.value()
    Dst = m3.position
    Azm = m1.position
    Elv = m2.position
    print(Dst,Azm,Elv)
    Sound.beep()

# 17=150mm
# 38=300mm
# Robot Params
#  COR=Centre of Rotation
#  Vertical distance table to COR: height=130mm
#  Horizontal offset from COR to needle axis: offset=33mm
#  Elevation is zero when the needle is parallel to the table
#  Azimuth is zero when the needle is pointing along the negative x axis
#
# Forward Kinematics:
#  projected_length=Dst*cos(Elv)
#  effective_length=sqrt(projected_length^2+offset^2)
#  azimuth_correction=atan2(offset,projected_length)
#  azimuth_efective=Azm-azimuth_correction
#  x=-effective_length*cos(azimuth_efective)
#  y= effective_length*sin(azimuth_efective)
#  z= Dst*sin(Elv)+height
#
# Measurements of LEGO model relative to 
#      Name          Azm,Elv,Dst,       X_CT         ,    Y_CT     ,       Z_CT
# Front Left Corner ,-22,-27,148, -24.857597007947618,125.337890625,-164.55509249983300
# Front Right Corner, 40,-32,136, -21.765711614238967,123.986328125,-284.10799438990176
# Back Right Corner , 23,-20,211,-108.338502638081820,126.013671875,-287.19987978361040
# Back Left Corner  ,-13,-20,218,-111.430388031790530,127.365234375,-167.64697789354165


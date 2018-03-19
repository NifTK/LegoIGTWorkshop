#!/usr/bin/env python3

from ev3dev.ev3 import *
import math

offset=33#mm
height=130#mm

def fk(Dst,Azm,Elv):
    projected_length=Dst*math.cos(math.radians(Elv))
    effective_length=math.sqrt(projected_length*projected_length+offset*offset)
    azimuth_correction=math.atan2(offset,projected_length)
    azimuth_efective=math.radians(Azm)-azimuth_correction
    x=-effective_length*math.cos(azimuth_efective)
    y= effective_length*math.sin(azimuth_efective)
    z= Dst*math.sin(math.radians(Elv))+height
    return [x,y,z]
    

m1 = LargeMotor('outB');    assert m1.connected, "Connect a motor to B port"
m2 = LargeMotor('outA');    assert m2.connected, "Connect a motor to A port"
ir = InfraredSensor();      assert ir.connected, "Connect a infrared sensor to any port"
ts = TouchSensor();         assert ts.connected, "Connect a touch sensor to any port"

m1.run_direct(duty_cycle_sp=0)
m2.run_direct(duty_cycle_sp=0)

# Put the infrared sensor into proximity mode.
ir.mode = 'IR-PROX'
while True:
    while not ts.value():    # Stop program by pressing touch sensor button
        # Infrared sensor in proximity mode will measure distance to the closest
        # object in front of it.
        ir_raw = ir.value()
    Dst = ir.value() * 300.0/38.0 # mm
    Azm = m1.position
    Elv = m2.position
    print(ir_raw,Azm,Elv,fk(Dst,Azm,Elv))
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
#                    Azm,Elv,Dst
# Front Left Corner: -22,-27,85+63
# Front Right Corner: 40,-32,73+63
# Back Right Corner:  23,-20,148+63
# Back Left Corner:  -13,-20,155+63

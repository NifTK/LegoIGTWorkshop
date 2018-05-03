#!/usr/bin/env python3

import socket
import sys
from ev3dev.ev3 import *
from time import sleep

m1 = LargeMotor('outB');    assert m1.connected, "Connect a motor to B port"
m2 = LargeMotor('outA');    assert m2.connected, "Connect a motor to A port"
m3 = MediumMotor('outC');   assert m3.connected, "Connect a motor to C port"

use_ir=False
try:
    ir = InfraredSensor();
    
    # Put the infrared sensor into proximity mode.
    ir.mode = 'IR-PROX'
    
    use_ir=True
except:
    print("Didn't find IR Sensor. Can't scan for towers.")
    use_ir=False

use_us=False
try:
    us = UltrasonicSensor();
    
    # Put the US sensor into distance mode.
    us.mode='US-DIST-CM'

    units = us.units
    # reports 'cm' even though the sensor measures 'mm'
    
    use_us=True
except:
    print("Didn't find US Sensor. Can't scan for towers.")
    use_us=False

#ts = TouchSensor();         assert ts.connected, "Connect a touch sensor to any port"

def decode_packet(data_string,packet_name):
    data_array=[]
    correct_name=False
    for s in data.split(','):
        try:
            # Attempt to turn the substring into a number
            data_array.append(float(s))
        except:
            # This is a string. Does it match the expected packet name?
            if s==packet_name:
                correct_name=True
    if correct_name:
        # If we got what we expected, return the extracted numbers
        return data_array
    # If we don't get what expected, just return an empty array
    return []

# Create a TCP/IP socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_address = ("", 3148)
sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#print >>sys.stderr, 'starting up on %s port %s' % server_address
print('starting up on ' + server_address[0] + ' on port ' , server_address[1])
sock.bind(server_address)
sock.listen(1)
while True:
    # Find connections
    #connection, client_address = sock.accept()
    (connection, client_address) = sock.accept()
    print('Accepted')
    try:
        data = connection.recv(999).decode()
        print("Received Packet: <"+data+">")
        packet=decode_packet(data,'lego')
        if len(packet)>=3:
            m1.run_to_abs_pos(position_sp=packet[1], speed_sp=100, stop_action="hold")
            m2.run_to_abs_pos(position_sp=packet[2], speed_sp=100, stop_action="hold")
            m2.wait_while('running',timeout=1500)   # Give the motor time to move
            m1.wait_while('running',timeout=1500)   # Give the motor time to move
            
            # Now execute the poke
            m3.run_direct(duty_cycle_sp=30)
            sleep(4)   # Give the motor time to move
            m3.run_direct(duty_cycle_sp=-30)
            sleep(4)   # Give the motor time to move
            m3.run_direct(duty_cycle_sp=0)
        else:
            pose_packet = decode_packet(data,'pose')
            if pose_packet != []:
                m1.run_direct(duty_cycle_sp=0)
                m2.run_direct(duty_cycle_sp=0)
                m3.run_direct(duty_cycle_sp=0)
                Dst = m3.position
                Azm = m1.position
                Elv = m2.position
                response = ('Dst='+repr(Dst)+', Azm='+repr(Azm)+', Elv='+repr(Elv))
                if use_ir:
                    response = response + ', IR=' + repr(ir.value())
                if use_us:
                    response = response + ', US=' + repr(us.value())
                connection.send(bytes(response, 'UTF-8'))

    except socket.error as e:
        print(e)

    except:
        connection.close()
        print('Connection Lost')

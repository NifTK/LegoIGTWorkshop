#!/usr/bin/env python3

import socket
import sys

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
        print("<"+data+">")
        print(decode_packet(data,'lego'))

    except:
        connection.close()
        print('Connection Lost')

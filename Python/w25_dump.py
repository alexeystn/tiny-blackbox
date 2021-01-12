import serial
import time
import numpy as np
from matplotlib import pyplot as plt


import serial.tools.list_ports

def find_com_port():
    for comport in serial.tools.list_ports.comports():
        print(comport.device)


port = '/dev/cu.usbserial-A50285BI'

with serial.Serial(port, 1500000, timeout=100) as ser:

    ser.write(b'S')
    d = ser.readline().decode()
    print(d)
    
    ser.write(b'1')
    d = ser.read(4000*256)
    b = np.frombuffer(d, dtype='uint8')
        

with open('output.bin', 'wb') as f:
    f.write(d)


import serial
import time
import numpy as np
from matplotlib import pyplot as plt


import serial.tools.list_ports

def find_com_port():
    for comport in serial.tools.list_ports.comports():
        print(comport.device)


port = '/dev/cu.usbserial-A50285BI'

with serial.Serial(port, 1500000, timeout=1) as ser, open('output.bin', 'wb') as f:

    ser.write(b's')
    d = ser.readline().decode()
    print(d)
    
    ser.write(b'd')  # [p] or [d]
    
    while True:
        d = ser.read(1000)
        if len(d) > 0:
            f.write(d)
        else:
            break
        
    

        
        
    #b = np.frombuffer(d, dtype='uint8')
        

    


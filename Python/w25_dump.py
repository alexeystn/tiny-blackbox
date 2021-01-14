import serial
from datetime import datetime
import serial.tools.list_ports

def find_com_port():
    for comport in serial.tools.list_ports.comports():
        print(comport.device)


port = '/dev/cu.usbserial-A50285BI'

filename = datetime.now().strftime('%Y%m%d_%H%M%S.bbl')
result = 0

with serial.Serial(port, 1500000, timeout=1) as ser, open(filename, 'wb') as f:
    result = 1
    print('Open ' + port + ' successfully')
    ser.write(b's')

    wait_counter = 0
    while wait_counter < 60:
        d = ser.readline().decode() 
        wait_counter += 1
        if len(d) > 0:
            print(d, end='')
            break
  
    if len(d) == 0:
        print('Serial port timeout')
    else:
        rx_counter = 0
        rx_counter_scaled = 0
        rx_counter_scaled_prev = 0
        while True:
            d = ser.read(1000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                
                rx_counter_scaled = rx_counter // (2**16)
                if (rx_counter_scaled > rx_counter_scaled_prev):
                    print('.', end='')
                    if (rx_counter_scaled % 16 == 0):
                        print(' {0:.0f} Mb'.format(rx_counter/(2**20)))
                rx_counter_scaled_prev = rx_counter_scaled
                
            else:
                break
        print('\n'+str(rx_counter) + ' bytes recieved')
    
if result == 0:
    print('Cannot open ' + port)
    


    


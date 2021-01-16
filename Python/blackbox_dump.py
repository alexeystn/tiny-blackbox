import serial
import serial.tools.list_ports
import time
from datetime import datetime
import json


def load_config():

    with open('config.json', 'r') as f:
        config = json.load(f)
    port = config['port']
    
    port_list = [c.device for c in serial.tools.list_ports.comports()]

    if not port in port_list:
        print('Cannot find serial port \'{0}\''.format(port))
        print('Select one of the availible ports:')
        for i, p in enumerate(port_list):
            print('{0}: {1}'.format(i+1, p))
        n = int(input())
    config['port'] = port_list[n-1]
    return config


def save_config(config):

    with open('config.json', 'w') as f:
        json.dump(config, f, indent=2)  


def check_header(header):

    if header[0:4] == b'\xdd\xcc\xbb\xaa':
        v = int.from_bytes(header[4:8], 'little')
        print()
        print('Flash memory: {0:.1f}% full'.format(v/10))
    else:
        'Incorrect device header.'


#port = '/dev/cu.usbserial-A50285BI'
#port = '/dev/cu.usbmodemFD14121'
#port = '/dev/cu.usbmodemFD131'


config = load_config()
    
filename = datetime.now().strftime('%Y%m%d_%H%M%S.bbl')
result = 0

with serial.Serial(config['port'], config['baudrate'], timeout=1) as ser, open(filename, 'wb') as f:

    result = 1
    print('Open ' + config['port'] + ' successfully')

    if config['use_passthrough'] != 0:
            print()
            print('=== Enter Betafligh CLI mode ===')
            
            ser.write(b'#\n')
            res = ser.readline()

            ser.write(('serialpassthrough ' + str(config['bf_uart_number'] - 1) + ' ' +
                       str(config['baudrate']) + '\n').encode())
            while (1):
                res = ser.readline()
                if len(res) == 0:
                    break
                s = res.decode()[:-2]
                if (len(s) > 0):
                    print(' >> ' + s)
            
            print('=== Exit Betafligh CLI mode ===')
            print()

    print('Hold button for 2 seconds', end='')
    
    wait_counter = 0
    while wait_counter < 60:
        print('.', end='')
        h = ser.read(8)
        wait_counter += 1
        if len(h) > 0:
            check_header(h)               
            break
  
    if len(h) == 0:      
        print()
        print('Serial port timeout')
    else:
        print('Downloading:')
        
    else:
        
        rx_counter = 0
        rx_counter_scaled = 0
        rx_counter_scaled_prev = 0
        
        while True: # print dots and megabytes
            d = ser.read(1000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                rx_counter_scaled = rx_counter // (2**16)
                if (rx_counter_scaled > rx_counter_scaled_prev):
                    print('.', end='')
                    f.flush()
                    if (rx_counter_scaled % 16 == 0):
                        print(' {0:.0f} Mb'.format(rx_counter/(2**20)))
                rx_counter_scaled_prev = rx_counter_scaled
                
            else:
                break
        print('\n'+str(rx_counter) + ' bytes recieved')
        print(filename + ' saved')
    
if result == 0:
    print('Cannot open ' + port)
else:
    save_config(config)
    


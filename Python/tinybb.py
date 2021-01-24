import serial
import serial.tools.list_ports
import time
from datetime import datetime
import json
import sys


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


def bf_enable_passthrough(ser, config):
    
    print()
    print('===== Betafligh CLI mode =====')
            
    ser.write(b'#\n')
    res = ser.readline()

    request_str = 'serialpassthrough ' + str(config['bf_uart_number'] - 1) + ' ' + str(config['baudrate']) + '\n'

    ser.write(request_str.encode())
    while (1):
        res = ser.readline()
        if len(res) == 0:
            break
        s = res.decode().strip()
        if (len(s) > 0):
            print(' >> ' + s)
            
    print('==============================')
    print()


def save_rx_data_to_file(ser, f):
    
    rx_counter = 0
    rx_counter_scaled = 0
    rx_counter_scaled_prev = 0

    print('Downloading:')
    print('Press ctrl+c to stop')

    try:
        while True: # print dots and megabytes
            d = ser.read(1000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                rx_counter_scaled = rx_counter // (2**16)
                if (rx_counter_scaled > rx_counter_scaled_prev):
                    print('.', end='', flush=True)
                    f.flush()
                    if (rx_counter_scaled % 16 == 0):
                        print(' {0:.0f} Mb'.format(rx_counter/(2**20)))
                rx_counter_scaled_prev = rx_counter_scaled
                
            else:
                break
    except KeyboardInterrupt:
        print()
        print('cancelled')

    print('\n'+str(rx_counter) + ' bytes recieved')
    print(filename + ' saved')    


def process_args():
    args = sys.argv
    if len(args) > 1:
        arg = args[1]
        if (len(arg) == 2) and (arg.startswith('-')):
            return arg[1]
    else:
        return None


def func_information(ser):
    
    ser.flushInput()
    ser.write('\n'.encode())
    time.sleep(0.1)
    ser.write('info\n'.encode())
    resp = ser.readline()
    if len(resp) > 0:
        print(resp.decode().strip())
    else:
        print('No responce from Blackbox')


def func_read(ser):
    ser.write('read\n'.encode())
    save_rx_data_to_file(ser, f)


def func_dump(ser):
    ser.write('dump\n'.encode())
    save_rx_data_to_file(ser, f)


def func_erase(ser):
    print('Erasing (~30 sec)')
    ser.write('erase\n'.encode())


def func_exit(ser):
    return


commands = dict({'i':['Information', func_information],
                 'r':['Read memory', func_read],
                 'd':['Dump full memory', func_dump],
                 'e':['Erase', func_erase],
                 'x':['Exit', func_exit] })


config = load_config()

arg = process_args()

if arg and not arg in commands:
    print('Wrong command line argument')
    sys.exit()

filename = 'Blackbox_Log_' + datetime.now().strftime('%Y%m%d_%H%M%S.bbl')
f = open(filename, 'wb')

result = 0

with serial.Serial(config['port'], config['baudrate'], timeout=1) as ser:

    result = 1
    print('Open ' + config['port'] + ' successfully')

    if config['use_passthrough'] != 0:
        bf_enable_passthrough(ser, config)
    
    func_information(ser)
    print()

    if arg:
        commands[arg][1](ser)
        
    else:
        for k in commands: print(k + ' - ' + commands[k][0])
        print()
        print('Enter command: ')
    
        while True:

            c = None
            
            if not c in commands:
                print('> ', end='')
                c = input()
            commands[c][1](ser)
            
            if c == 'x':
                break

    
if result == 0:
    print('Cannot open ' + port)
else:
    save_config(config)

print()


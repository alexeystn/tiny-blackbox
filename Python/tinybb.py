import sys
import time
import json
from datetime import datetime
import serial
import serial.tools.list_ports


def load_config():
    with open('config.json', 'r') as f:
        config = json.load(f)
    available_ports = [c.device for c in serial.tools.list_ports.comports()]
    if not config['port'] in available_ports:
        print('Cannot find serial port \'{0}\''.format(config['port']))
        print('Select one of the available ports:')
        for i, port in enumerate(available_ports):
            print('{0}: {1}'.format(i+1, port))
        print('> ', end='')
        n = int(input())
        config['port'] = available_ports[n-1]
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
    while True:
        res = ser.readline()
        if len(res) == 0:
            break
        s = res.decode().strip()
        if len(s) > 0:
            print(' >> ' + s)
    print('==============================')
    print()
    time.sleep(1)


def save_rx_data_to_file(ser):
    rx_counter = 0
    rx_counter_scaled = 0
    rx_counter_scaled_prev = 0
    filename = 'Blackbox_Log_' + datetime.now().strftime('%Y%m%d_%H%M%S.bbl')
    f = open(filename, 'wb')
    print('Downloading:')
    print('Press ctrl+c to stop')
    try:
        while True: # print dots and megabytes
            d = ser.read(1000)
            if len(d) > 0:
                rx_counter += len(d)
                f.write(d)
                rx_counter_scaled = rx_counter // (2**16)
                if rx_counter_scaled > rx_counter_scaled_prev:
                    print('.', end='', flush=True)
                    f.flush()
                    if rx_counter_scaled % 16 == 0:
                        print(' {0:.0f} Mb'.format(rx_counter/(2**20)))
                rx_counter_scaled_prev = rx_counter_scaled
            else:
                break
    except KeyboardInterrupt:
        print()
        print('cancelled')
    f.close()
    print('\n'+str(rx_counter) + ' bytes received')
    print(f.name + ' saved')    


def process_args():
    arguments = sys.argv
    if len(arguments) > 1:
        a = arguments[1] # skip [0] .py script name
        if (len(a) == 2) and (a.startswith('-')):
            return a[1] # remove dash
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
        print('No response from Blackbox. Check if Read mode is ON. ')


def func_read(ser):
    ser.write('read\n'.encode())
    save_rx_data_to_file(ser)


def func_dump(ser):
    ser.write('dump\n'.encode())
    save_rx_data_to_file(ser)


def func_erase(ser):
    print('Erasing, wait ~30 seconds')
    ser.write('erase\n'.encode())


def func_exit(ser):
    return


def main():
    config = load_config()
    commands = dict({'i':['Information', func_information],
                     'r':['Read memory', func_read],
                     'd':['Dump full memory', func_dump],
                     'e':['Erase', func_erase],
                     'x':['Exit', func_exit] })
    cli_argument = process_args()
    if cli_argument and not cli_argument in commands:
        print('Wrong command line argument')
        sys.exit()
    serial_port_result = 0
    with serial.Serial(config['port'], config['baudrate'], timeout=1) as ser:
        serial_port_result = 1
        print('Open ' + config['port'] + ' successfully')
        if config['use_passthrough'] != 0:
            bf_enable_passthrough(ser, config)
        func_information(ser)
        print()
        if cli_argument:
            commands[cli_argument][1](ser)
        else:
            for k in commands: print(k + ' - ' + commands[k][0])
            print()
            print('Enter command: ')
            while True:
                user_command = None
                while not user_command in commands:
                    print('> ', end='')
                    user_command = input()
                commands[user_command][1](ser)
                if user_command == 'x':
                    break

    if serial_port_result == 0:
        print('Cannot open ' + config['port'])
    else:
        save_config(config)
    print()


if __name__ == "__main__":
    main()

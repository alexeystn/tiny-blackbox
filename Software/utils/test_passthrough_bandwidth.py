import serial.tools.list_ports

# available_ports = [c.device for c in serial.tools.list_ports.comports()]
# print(available_ports)

port_input = '/dev/cu.usbmodem0x80000001'
port_output = '/dev/cu.usbserial-A50285BI'

serial_input = serial.Serial(port_input, 500000, timeout=1)
serial_output = serial.Serial(port_output, 500000, timeout=1)

print('Ready to test:')
if input():  # switch to passthrough
    serial_input.write(b'#\n')
    serial_input.readline()
    serial_input.write(b'serialpassthrough 0 500000\n')
    while True:
        res = serial_input.readline()
        if len(res) == 0:
            break
        print(' >> ' + res.decode().strip())

num_bytes = 10000

b_tx = ''.join(['{0:04d}'.format(i) for i in range(num_bytes)]).encode()
serial_output.write(b_tx)

b_rx = serial_input.read(len(b_tx))

print('TX:', len(b_tx), 'RX:', len(b_rx))

if len(b_tx) == len(b_rx):
    print('SUCCESS!')
else:
    print('FAIL!')

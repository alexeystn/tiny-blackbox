# Send continuous ASCI sequence of incrementing numbers to Serial port
# Each number is encoded with 8 characters:
# '00000000', '00000001', '00000002', ..... '02097152'

import time
import serial
import serial.tools.list_ports

full_memory_size = 128 * 1024 * 1024 // 8  # 128 MBit flash chip
bytes_per_number = 8

# Test in normal mode:
# packet_length = 50  # x 8 bytes
# packet_interval_sec = 0.03

# Test with emulated write delay:
packet_length = 500  # x 8 bytes
packet_interval_sec = 0.1


def encode_number(n):
    return '{0:08d}'.format(n).encode()


class SpeedMeasure:
    previous_timestamp = 0
    counter = 0

    def put(self, n):
        self.counter += n
        current_timestamp = time.time()
        if current_timestamp - self.previous_timestamp > 1:  # print 1 time / second
            t_diff = current_timestamp - self.previous_timestamp
            speed = self.counter / t_diff
            self.counter = 0
            self.previous_timestamp = current_timestamp
            print('{0:.0f} kbit/s'.format(speed / 1000 * 8), end='\t')
            return 1
        return 0


sm = SpeedMeasure()

available_ports = [c.device for c in serial.tools.list_ports.comports()]
print('Select one of the available ports:')
for i, port in enumerate(available_ports):
    print('{0}: {1}'.format(i + 1, port))
print('>> ', end='')
p = int(input())
port_name = available_ports[p - 1]

packet = b''

with serial.Serial(port_name, baudrate=1500000) as ser:
    for i in range(full_memory_size // bytes_per_number):
        packet += encode_number(i)
        if (i + 1) % packet_length == 0 or (i+1) == (full_memory_size // bytes_per_number):
            ser.write(packet)
            packet = b''
            time.sleep(packet_interval_sec)
            if sm.put(bytes_per_number * packet_length):
                print('{0:.1f}%'.format(i / (full_memory_size // bytes_per_number) * 100))

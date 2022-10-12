# Check if log created with 'test_sequence_transmit'
# was successfully recorded and read from flash.
#
# BBL file must be in the same directory

import os
import sys

file_list = [f for f in os.listdir() if f.endswith('.bbl')]

if len(file_list) == 0:
    print('No .bbl files found')
    input()
    sys.exit(0)

file_list.sort()  
print('Select file:')
for i, file in enumerate(file_list):
    print('{0}: {1}'.format(i+1, file))
if len(file_list) == 1:
    filename = file_list[0]
else:
    print('>> ', end='')
    n = int(input())
    filename = file_list[n-1]

with open(filename, 'rb') as f:
    data = f.read()

bytes_per_count = 8
size = len(data)//bytes_per_count
error_count = 0

for i in range(size):
    fragment = data[i*bytes_per_count:(i+1)*bytes_per_count]
    original = '{0:08d}'.format(i).encode()
    if fragment != original:
        print(original, '!=', fragment)
        error_count += 1
        if error_count > 20:
            print('Too many errors')
            break
        
if error_count == 0:
    print('No errors detected')

input()

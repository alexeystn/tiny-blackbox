# Check if log created with 'test_sequence_transmit'
# was successfully recorded and read from flash.

filename = '../xxx.bbl'

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

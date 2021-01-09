import serial
import time
import numpy as np
from matplotlib import pyplot as plt



with open('output.bin', 'rb') as f:
    print(1)
    fs = f.read()


s = 'End of log'

v = fs.find(s.encode())


with open('bflog.bbl', 'wb') as f:
    f.write(fs[:(v+len(s))])

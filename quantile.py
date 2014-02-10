#!/usr/bin/env python
# Takes as input a column of values, and produce the list
# of quantiles from 1 to 99.
#
import sys
import numpy as np

if __name__ == "__main__":
    array = []
    for line in sys.stdin.readlines():
        line = line.strip()
        try:
            num = float(line)
            array.append(num)
        except:
            print("Error!")
            print(num)
    array = np.array(array)
    for perc in np.arange(0, 100, 1):
        sys.stdout.write("%f\t%f\n" % (perc, np.percentile(array, int(perc), axis=None)))
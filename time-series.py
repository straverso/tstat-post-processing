#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Tstat post-processing tool
# 
# Authors: Ignacio Bermudez <ignaciobermudez@gmail.com>
#          Stefano Traverso <stefano.traverso@polito.it>          
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see <http://www.gnu.org/licenses/>.
#

"""
Post processing tool for Tstat logs to create time series.

This script takes as input a Tstat log (tcp_complete, http, etc.).

"""

import mmap
import sys
import os
import re
import gzip
from optparse import OptionParser
import multiprocessing as mp
import pandas as pd
import numpy as np
import regexp_filter
import datetime
from blist import blist
import gc
import objgraph

def get_fields_to_print(fields):
    """Converts the list of columns to print in the proper format for the output file.
    """
    fieldsArray = fields.split(",")
    out_string_for_write = ''
    counter = 0
    for field in fieldsArray:
        out_string_for_write += '{'+str(counter)+'} '
        counter += 1
    out_string_for_write = out_string_for_write[:-1]+"\n"
    return out_string_for_write, fieldsArray

def read_tstat_log(filename, outfilename, fields, binsize):
    """This function is called for each detected tstat log present in the input folder. Each input log is
    handled by an independent subprocess, so that all the available cores are employed.
    """
    # Open current input and output file
    infile = open(filename, "r")
    outfile = open(outfilename, "w")        
    try:
        # # Check the file is gzipped
        if filename.endswith(".gz"):
            infile = gzip.open(filename, 'r')
        
        print ("Printing %s of log %s" % (fields, filename))

        out_string_for_write, fieldsArray = get_fields_to_print(fields)
        fieldsArray.insert(0, "timestamp")
        fieldsArray.insert(1, "comlp")

        line = infile.readline()
        if line[0] == '#':
            line = infile.readline()
        record = tstat.tstatrecord(line)
        value = [getattr(record, field)  for field in fieldsArray]
        current_time = (float(value[0])+float(value[1]))/1000.0
        current_tm = datetime.datetime.fromtimestamp(int(current_time))
        last_thr = current_time
        threshold = int(binsize)
        current_tm = current_tm - datetime.timedelta(minutes=(current_tm.minute % 5) - 1,
                            seconds=current_tm.second,
                            microseconds=current_tm.microsecond)
        date_range = pd.date_range(start=current_tm,
                            periods=int(3720.0/threshold), 
                            freq=str(threshold)+'s')
        metric_array = []
        counter = 0

        while line:
            record = tstat.tstatrecord(line)
            value = [getattr(record, field)  for field in fieldsArray]
            if datetime.datetime.fromtimestamp(current_time) < date_range[counter]:
                current_time = (float(value[0])+float(value[1]))/1000.0
                metric_array.append(float(value[2]))
            else:
                # outfile.write("%d %d %d %d\n" % (current_time, s2c_bytes, c2s_bytes, flows))
                last_thr = current_time
                np_array = np.array(metric_array)
                outstring = "%s %d %f %f %f %f\n" % (date_range[counter], len(np_array), np_array.sum(), np_array.mean(), np.median(np_array), np.std(np_array))
                print(outstring[:-1])
                outfile.write(outstring)
                counter += 1
                del metric_array[:]
                del np_array
                metric_array = [float(value[2])]
                
            line = infile.readline()
    except:
        print sys.exc_info()[0]
    finally:
        infile.close()
        outfile.close()
    return  

def options():
    parser = OptionParser()
    parser.add_option('-o','--outsuffix', dest='outsuff', help='Output suffix filename')
    parser.add_option('-i','--inname', dest='insuff', help='Input filename')
    parser.add_option('-r','--read', dest='read', help='Input folder')
    parser.add_option('-l','--log', dest='logtype', help='Kind of log to process: http, tcp, udp, mm, skype, streaming, chat.')
    parser.add_option('-f','--tstat-field', dest='fields', help='Tstat field to serialize. E.g. c2sdata')
    parser.add_option('-b','--binsize', dest='binsize', help='The size of the bin to consider')
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    (a, b) = parser.parse_args()
    return a

def main():
    """Process each (zipped or not) log in the folder and apply regexp on a given column. Only
    specified columns are printed out.
    """
    opt = options()
    indirectory = os.path.join("./", opt.read)
    os.chdir(indirectory)
    
    log = "tstat_tcp_complete"
    if opt.logtype == "tcp":
        log = 'tstat_tcp_complete'
    elif opt.logtype == "http":
        log = 'tstat_http'
    elif opt.logtype == "streaming":
        log = 'tstat_streaming'
    else:
        print("Error! Log type do not exist.")
        sys.exit(1)

    global tstat 
    tstat = __import__(log)

    print("Start processing...")
    read_tstat_log("%s%s" % (opt.read, opt.insuff), "%s%s%s" % (opt.read, opt.insuff, opt.outsuff), opt.fields, opt.binsize)
    print("End.")

if __name__ == "__main__":
    main()


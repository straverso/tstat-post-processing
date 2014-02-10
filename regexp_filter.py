#!/usr/bin/python
# -*- coding: utf-8 -*-

"""@package regexp-filter
This script applies a given regular expression (input) on a specified column (input) of a tstat log.
It handles a tstat log (zipped or not) at time and supports multiprocessing by default.
"""

import mmap
import sys
import os
import re
import gzip
from optparse import OptionParser
import multiprocessing as mp


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


def matching(line, tcols):
    """Extract the selected columns out of a tstat record (a line of a tstat log).
    If all columns are specified, the whole record considered for the match. 
    """
    if tcols != "all":
        record = tstat.tstatrecord(line)
        to_match = " ".join([getattr(record, str(tcol)) for tcol in tcols.split(",")])
    else:
        to_match = line
    return to_match

def read_tstat_log((filename, regex, outfilename, tcols, fields)):
        """This function is called for each detected tstat log present in the input folder. Each input log is
        handled by an independent subprocess, so that all the available cores are employed.
        """
        # if not terminating.is_set():
        # Open current input and output file
        infile = os.open(filename, os.O_RDONLY)
        outfile = open(outfilename, "w")        
        try:
            map = mmap.mmap(infile, 0, prot=mmap.PROT_READ)
            inmap = map
            # Check the file is gzipped
            if filename.endswith(".gz"):
                inmap = gzip.GzipFile(mode="r", fileobj=map)
            
            print ("Printing %s of log %s with %s on %s" % (fields, filename, regex, tcols))

            out_string_for_write, fieldsArray = get_fields_to_print(fields)

            line = inmap.readline()

            while line[0] == '#':
                line = inmap.readline()
            print  tcols
            to_match = matching(line, tcols)
            
            while line:
                to_match = matching(line, tcols)
                if re.search(regex, to_match):
                    record = tstat.tstatrecord(line)
                    if "all" not in fieldsArray:
                        # print out_string_for_write, fieldsArray, [getattr(record, field)  for field in fieldsArray]
                        outfile.write(out_string_for_write.format(*[getattr(record, field)  for field in fieldsArray]))
                    else:
                        # print out_string_for_write, fieldsArray, line
                        outfile.write(line)
                line = inmap.readline()
            map.close()
            if filename.endswith(".gz"):
                inmap.close()
        # except:
        #     print line
        #     # terminating.set()
        finally:
            os.close(infile)
            outfile.close()
    # return  

def initializer(terminating_):
    """This places terminating in the global namespace of the worker subprocesses.
    This allows the worker function to access `terminating` even though it is
    not passed as an argument to the function. Good to terminate the script in any
    moment with Crtl+C."""
    global terminating
    terminating = terminating_  

def options():
    parser = OptionParser()
    parser.add_option('-p','--prefix', dest='pre', help='Output prefix/folder filename')
    parser.add_option('-o','--outsuffix', dest='outsuff', help='Output suffix filename')
    parser.add_option('-i','--insuffix', dest='insuff', help='Input suffix filename (.log, .gz, etc.)')
    parser.add_option('-r','--read', dest='read', help='Read from tstat log file')
    parser.add_option('-l','--log', dest='logtype', help='Kind of log to process: http, tcp, udp, mm, skype, streaming, chat.')
    parser.add_option('-e','--regexp', dest='regex', help='Regular expression to use')
    parser.add_option('-c','--tstat-match', dest='tcols', help='Tstat fields to match.')
    parser.add_option('-f','--tstat-print', dest='fields', help='Tstat fields to print.')
    parser.add_option('-I','--showip', dest='ip', help='If "y" add server IP address to outfile', default="f")
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    (a, b) = parser.parse_args()
    return a



def main():
    """Process each (zipped or not) log in the folder and apply regexp on a given column. Only
    specified columns are printed out.
    """
    # terminating = mp.Event()
    opt = options()
    indirectory = os.path.join("./", opt.read)


    try:
    	# Get The correct files in directory
    	files_in_dir = [files for files in os.listdir(indirectory) if files.endswith(opt.insuff)]
	if len(files_in_dir) == 0:
	    raise OSError
    	files_in_dir.sort()
    	os.chdir(indirectory)
    except OSError:
	print("Error! Input dir or files do not exist.")
	sys.exit(1)
	
    
    showip = False
    if opt.ip == "y":
        showip = True

    log = "tstat_tcp_complete"
    if opt.logtype == "tcp":
        log = 'tstat_tcp_complete'
    elif opt.logtype == "http":
        log = 'tstat_http_complete'
    elif opt.logtype == "streaming":
        log = 'tstat_streaming'
    else:
        print("Error! Log type do not exist.")
        sys.exit(1)

    global tstat 
    tstat = __import__(log)

    # pool = mp.Pool(initializer=initializer, initargs=(terminating, ))

    for f in files_in_dir:
       read_tstat_log((f, opt.regex, "%s%s%s" % (opt.pre, f.replace(".gz", ""), opt.outsuff), opt.tcols, opt.fields))

    # try:
        # pool.map(read_tstat_log, [(f, opt.regex, "%s%s%s" % (opt.pre, f.replace(".gz", ""), opt.outsuff), opt.tcols, opt.fields) for f in files_in_dir])
        # pool.close()
    # except KeyboardInterrupt:
        # pool.terminate()
        # print("Interrupted!")
    # finally:
        # pool.join()
    print "End."

if __name__ == "__main__":
    main()

# (c) 2013-2014 mPlane Consortium (http://www.ict-mplane.eu)
#               Author: Stefano Traverso
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

import sys
import os
import multiprocessing as mp
import time
import subprocess
import signal
import logging
import datetime
from unidecode import unidecode
import psutil
from optparse import OptionParser

logging.basicConfig(format='%(asctime)s %(message)s', level=logging.INFO)

class TimeoutError(Exception):
    pass

class timeout:
    def __init__(self, seconds=1, error_message='Timeout'):
        self.seconds = seconds
        self.error_message = error_message
    def handle_timeout(self, signum, frame):
        raise TimeoutError(self.error_message)
    def __enter__(self):
        signal.signal(signal.SIGALRM, self.handle_timeout)
        signal.alarm(self.seconds)
    def __exit__(self, type, value, traceback):
        signal.alarm(0)

def tail_tstat_log(child_pipe, filename, timeoutset, pid):
    """This function is called for each detected tstat log present in the input folder. Each input log is
    handled by an independent subprocess, so that all the available cores are employed.
    """
    subp = subprocess.Popen('tail -n100 -f %s' % filename, stdout=subprocess.PIPE, shell=True)
    subpfile = open("/tmp/log_to_tcp_tail_pid.txt", "w")
    subpfile.write("%d\n" % subp.pid)
    subpfile.close()
    first = True
    while True:
        try:
            with timeout(seconds=((int(timeoutset)+1)*60)):
                line = subp.stdout.readline().decode("ascii", 'ignore')
                if line.startswith("#") or first == True:
                    child_pipe.send("".join("!"+filename + " " + line))
                    first = False
                else:
                    child_pipe.send(line)
                # print(line[:-1])
        except TimeoutError:
            logging.warning("Timeout! Log ended now. Closing the read process for %s..." % filename)
            subp.terminate()
            return
        # sleep(0.001)
    subp.terminate()
    return

def initializer(terminating_):
    """This places terminating in the global namespace of the worker subprocesses.
    This allows the worker function to access `terminating` even though it is
    not passed as an argument to the function. Good to terminate the script in any
    moment with Crtl+C."""
    global terminating
    terminating = terminating_  

def run(child_pipe, logtype, logtime, logfolder):

    terminating = mp.Event()
    files_in_dir = None
    # current_dir = sorted(os.listdir(opt.read), key=os.path.getctime)[-1]
    current_dir = logfolder + sorted([f for f in os.listdir(logfolder) if ".out" in f])[-1]
    # current_dir = commands.getstatusoutput("ls -tr "+ opt.read +" | grep -v delete | grep -v stderr")[1].split("\n")[-1]
    logging.info("Reading log %s" % (current_dir))
    counter = 0
    # Launch exporter on current_dir
    p = mp.Process(target=tail_tstat_log, args=(child_pipe, os.path.abspath(current_dir+"/"+logtype), logtime, counter))
    p.start()

    while True:
        # Get the latest log in the directory
        files_in_dir = sorted([f for f in os.listdir(logfolder) if ".out" in f])
        # files_in_dir = commands.getstatusoutput("ls -tr "+ opt.read +" | grep -v delete | grep -v stderr")[1].split("\n")
        if len(files_in_dir) == 0:
            raise OSError
        new_dir = logfolder + files_in_dir[-1]
        if new_dir != current_dir:
            # New File!!
            logging.info("New log to read! %s " % (os.path.abspath(new_dir+"/"+logtype)))
            counter += 1
            p_old = p
            # Terminate last process
            logging.info("Kill old log reader! %s " % (os.path.abspath(current_dir+"/"+logtype)))
            parent = psutil.Process(p_old.pid)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()
            # # Start new one
            logging.info("Start new log reader! %s " % (os.path.abspath(new_dir+"/"+logtype)))
            p = mp.Process(target=tail_tstat_log, args=(child_pipe, os.path.abspath(new_dir+"/"+logtype), logtime, counter))
            p.start()
            # Update variables
            current_dir = new_dir            
        time.sleep(0.1)
 
    parent = psutil.Process(p.pid)
    for child in parent.children(recursive=True):
        child.kill()
    parent.kill()
    # for f in files_in_dir:
    #     print(f)
 
    print("End.")

def close_and_create_new_log(line, path, logtype, outputfile):
    new_log = [x for x in line.split()[0][1:].split("/") if x.startswith("2")][0]
    filename = path + new_log
    if not os.path.exists(filename):
        os.makedirs(filename)
        logging.info("New log created! %s" % filename)
        if outputfile:
            outputfile.close()
        outputfile = open(filename+"/"+logtype, "w")
    outputfile.write("\t".join(line.split()[1:])+"\n")
    return outputfile

def options():
    help_text = """    
    Online log merger. 
    """
    parser = OptionParser(usage=help_text)
    parser.add_option('-i','--inlogs', dest='log_folders', help='List of paths to logs to merge separated by commas (,)')
    parser.add_option('-o','--outlog', dest='outpath', help='Output path for log merged')
    parser.add_option('-l','--logtype', dest='log_type', help='Kind of logs to merge (log_tcp_complete, log_http_complete, etc.)')
    parser.add_option('-t','--logtime', dest='log_time', help='Log length in time (minutes)')
    (options, args) = parser.parse_args()
    if len(sys.argv) == 1:
        parser.print_help()
        sys.exit(1)
    (a, b) = parser.parse_args()
    return a

def main():
    opt = options()
    log_type = opt.log_type
    log_folders = [folder+"/" for folder in opt.log_folders.split(",")]
    print(log_folders)
    outpath = opt.outpath+"/"
    log_time = int(opt.log_time)

    processes = {}
    parent_pipes = {}
    children_pipes = {}
    counter = 0
    for log_folder in log_folders:
        parent_pipes[counter], children_pipes[counter] = mp.Pipe(duplex = False)
        p = mp.Process(target=run, args=(children_pipes[counter], log_type, log_time, log_folder))
        processes[counter] = p
        p.start()
        counter += 1

    outputfile = None
    lines = [parent_pipes[index].recv() for index in parent_pipes]
    while True:
        while sum([1 if len(line) > 0 else 0 for line in lines]) < len(lines):
            for line in lines:
                if len(line) == 0:
                    lines[lines.index(line)] = parent_pipes[lines.index(line)].recv()
        newlogflagindex = [lines.index(line) for line in lines if line.startswith("!") ]
        if len(newlogflagindex) > 0:
            newlogflag = lines[newlogflagindex[0]] 
            outputfile = close_and_create_new_log(newlogflag, outpath, log_type, outputfile)
            lines[newlogflagindex[0]] = parent_pipes[newlogflagindex[0]].recv()
        else:
            try:
                lineArrays = [line.split() for line in lines] 
                timestamps = [float(lineArray[4])  for lineArray in lineArrays]
                min_index = timestamps.index(min(timestamps))
                outputfile.write(lines[min_index])
                lines[min_index] = parent_pipes[min_index].recv()
            except:
                print(lines)
                exit()

if __name__ == "__main__":
    main()

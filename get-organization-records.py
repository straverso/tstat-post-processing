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
Post processing tool for Tstat logs.

This script takes as input a Tstat log (tcp_complete, http, etc.), 
and an organization name, e.g. Amazon.
It prints out all Tstat records whose IPsrc or IPdst belong the
specified organization.
It also implements HTTP knocking procedure and reverse nslookup 
(results are appended to Tstat record).
Filtering is based on the MaxMind database (given as input).

"""

import sys
from multiprocessing import Process, JoinableQueue
import multiprocessing
import tstat_tcp_complete as tstat
import objectCache
import socket
import struct
import commands
import thread
import threading
import re
import cdnscan
from optparse import OptionParser
import GeoIP

class orgThread (Process):
    def __init__(self,threadID,inqueue,outqueue):
        Process.__init__(self)
        self.daemon = True
	self.threadID = threadID
        self.queue = inqueue
        self.out = outqueue
        self.not_organization_cache = objectCache.objectCache(100000)
        self.organization_cache = objectCache.objectCache(10000)
	self.processed_lines = 0
        self.not_organization_c = 0
        self.organization_c = 0
	self.not_organization_hit = 0
        self.organization_hit = 0
	print >> sys.stderr, "[THREAD INIT %d]"%(self.threadID)

    def run(self):
        print >> sys.stderr, "[THREAD STARTED %d]"%(self.threadID)
        while True:
            line = self.queue.get()
            if line is None:
                 self.queue.task_done()
                 return
                #print >> sys.stderr, "[THREAD %d number of flows processed: %d not organization cache size: %d organization cache size]"%(self.threadID, self.processed_lines, self.not_organization_cache.size(), self.amazon_cache.size())
            line = re.sub(r'\n$','',line)
            record = tstat.tstatrecord(line)
            sip = record.sip
            ip_range = re.sub(r'\.\d+$', '',sip)
            self.processed_lines += 1
            if self.processed_lines%10000 == 0:
                print >> sys.stderr, "[THREAD %d %s Flows %d NOT %s FLOWS %d %s HIT %d NOT %s HIT %d]"%(self.threadID, to_search, self.organization_c, to_search, self.not_organization_c, to_search, self.organization_hit, to_search, self.not_organization_hit)
                self.organization_c = 0
                self.organization_hit = 0
                self.not_organization_c = 0
                self.not_organization_hit = 0
            if not self.not_organization_cache.get(ip_range) == None:
                self.not_organization_c += 1
                self.not_organization_hit += 1
                self.queue.task_done()
                continue
            elif not self.organization_cache.get(ip_range) == None:
                self.organization_c += 1
                self.organization_hit += 1
                self.out.put((sip, line, record, self.organization_cache.get(ip_range)[1]))
                self.queue.task_done()
                continue
            org = getIPOrg(sip) 
           # print org, sip, line
            if org == None:
                self.not_organization_c += 1
                self.not_organization_cache.put(ip_range, False)
                self.queue.task_done()
                continue
            org = org.lower()
            if re.search(to_search,org):
                self.organization_c += 1
                self.organization_cache.put(ip_range, org)
                self.out.put((sip, line, record, org))
            else:
                self.not_organization_c += 1
                self.not_organization_cache.put(ip_range, False)
            self.queue.task_done()

    def getIPOrg(ip):
        return gi.org_by_addr(ip)
#        sip = struct.unpack('>I', socket.inet_aton(ip))[0]
#        q = "SELECT start_ip, end_ip, org FROM geoiporg WHERE start_ip<"+str(sip)+" ORDER BY start_ip DESC LIMIT 1"
#        con.query(q)
#        r = con.use_result()
#        row = r.fetch_row()[0]
#        end_ip = int(row[1])
#        if end_ip > sip:
#            return row[2]
#        else:
#            return None

class lookupThread (threading.Thread):
    def __init__(self,inqueue,outqueue):
        threading.Thread.__init__(self)
        self.queue = inqueue
        self.out = outqueue
        self.organization_ip_cache = objectCache.objectCache(10000)

    def run(self):
        while True:
            val = self.queue.get()
            if val is None:
                self.queue.task_done()
                return
            (sip, line, record, org) = val
            '''
            Cached Organization name, just reply
            '''
            if not self.organization_ip_cache.get(sip) == None:
                self.out.put((sip, line, record, self.organization_ip_cache.get(sip)[1]))
                self.queue.task_done()
                continue

            '''
            Organization IP address, then save type of server
            '''
            reverse = commands.getoutput('nslookup '+record.sip)
            m = re.search(r'name\s=\s(.*)$',reverse,flags=re.MULTILINE)
            if m:
                name = m.group(1)
                self.organization_ip_cache.put(sip, name)
                self.out.put((sip, line, record, name)) 
            else:
                server = cdnscan.scanServer(sip)
                if not server == None:
                    name = 'server-type-'+server
                    self.organization_ip_cache.put(sip, name)
                    self.out.put((sip, line, record, name))
                else:
                    self.out.put((sip, line, record, 'organization-no-name'))
                    self.organization_ip_cache.put(sip, 'organization-no-name')
            self.queue.task_done()
    
def read_tstat_log(fh, out_queue):
    for line in fh.xreadlines():
        if not line[0]=='#':
            line = re.sub(r'\n$','',line)
            record = tstat.tstatrecord(line)
            out_queue.put((record.sip, line, record))

def read_output(in_queue):
    while True:
        tuple = in_queue.get()
        if tuple is None:
            in_queue.task_done()
            return
        (sip, line, record, name) = tuple
        print line, name
        in_queue.task_done()

def main():
    opt = options()
    db_in_queue = JoinableQueue(10000)
    db_out_queue = JoinableQueue(100000)
    lookup_out_queue = JoinableQueue(100000)
    org_threads = multiprocessing.cpu_count()
    org_t = []
    lookup_threads = 10
    lookup_t = []
    global gi 
    gi = GeoIP.open(opt.geoip_path, GeoIP.GEOIP_STANDARD)

    global to_search
    to_search = opt.to_search
    
    read_output_t = Process(target=read_output, args=(lookup_out_queue,))
    read_output_t.daemon = True
    read_output_t.start()
    for i in range(org_threads):
        t = orgThread(i, db_in_queue, db_out_queue)
#        t.setDaemon(True)
        org_t.append(t)
        t.start()
    for i in range(lookup_threads):
        t = lookupThread(db_out_queue, lookup_out_queue)
        t.setDaemon(True)
        lookup_t.append(t)
        t.start()
    if opt.read:
        fh = open(opt.read,'r')
        if opt.read.endswith(".gz"):
            fh = os.popen("zcat " + opt.read)
    else:
        fh = sys.stdin

#    thread.start_new_thread(read_output, (lookup_out_queue, ))
    
    read_lines = 0
    for line in fh:
        if not line[0]=='#':
            db_in_queue.put(line)
            read_lines += 1
            if read_lines%10000 == 0:
                print >> sys.stderr, "[Read lines %d]"%(read_lines)
#            line = re.sub(r'\n$','',line)
#            record = tstat.tstatrecord(line)
#            db_in_queue.put((record.sip, line, record))
    for i in range(org_threads):
        db_in_queue.put(None)
    
    db_in_queue.join()

    for i in range(lookup_threads):
        db_out_queue.put(None)

    db_out_queue.join()

    lookup_out_queue.put(None)
    lookup_out_queue.join()

    for i in range(org_threads):
        org_t[i].join(2)
    for i in range(lookup_threads):
        lookup_t[i].join(2)
    read_output_t.join()

def getIPOrg(ip):
    return gi.org_by_addr(ip)

def options():
    help_text = """    
    Example for tcp_log_complete: print records which refer to "acme" organization 
    python2.7 get-organization-records.py -r /path/to/log/folder/log_tcp_complete.gz -g /path/to/MMdb/GeoIPOrg.dat -o acme > /tmp/output.txt

    """
    parser = OptionParser(usage=help_text)
    parser.add_option('-p','--prefix', dest='pre',help='Output prefix filename')
    parser.add_option('-r','--read', dest='read',help='Read from tstat log file')
    parser.add_option('-g','--geoip', dest='geoip_path',help='Path to the GeoIP db')
    parser.add_option('-o','--org', dest='to_search',help='Organization name to look for')
    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    (a, b) = parser.parse_args()
    return a

main()

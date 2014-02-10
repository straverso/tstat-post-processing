#!/usr/bin/python

import httplib
import socket

def scanServer(host, port=80, method='HEAD', path='/', timeout=10, ssl=False):
    try:
        conn = None
        if ssl:
            conn = httplib.HTTPSConnection(host, 443)
#            conn = httplib.HTTPSConnection(host, 443, timeout=timeout)
        else:
            conn = httplib.HTTPConnection(host, port)
#            conn = httplib.HTTPConnection(host, port,timeout=timeout)
        conn.request(method,path)
        resp = conn.getresponse()
        server = resp.getheader('server')
        conn.close()
        return server
    except socket.timeout:
        if not ssl:
            return scanServer(host,ssl=True)
        return host+" timeout"
    except httplib.BadStatusLine:
        if not ssl:
            return scanServer(host, ssl=True)
        return host+" BadStatusResponse"
    except socket.error:
        return host+" Socket Error"

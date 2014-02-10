#!/usr/bin/python

class tstatrecord:
    def __init__(self, line):
        t = line.split()
        self.c_ip           = t[0]
        self.c_port         = t[1]
        self.s_ip           = t[2]
        self.s_port         = t[3]
        self.time_abs       = t[4]
        self.method         = ""
        self.hostname       = ""
        self.fqdn           = ""
        self.path           = ""
        self.referer        = ""
        self.user_agent     = ""
        self.HTTP           = ""
        self.response       = ""
        self.content_len    = ""
        self.content_type   = ""
        self.server         = ""
        self.range          = ""
        if t[5] != "HTTP":
            # Client Short description
            self.method         = t[5]        
            self.hostname       = t[6]      
            self.fqdn           = t[7]  
            self.path           = t[8]  
            self.referer        = t[9]      
            self.user_agent     = str(t[10:-1])
        else:
            # Server Short description
            self.HTTP           = t[5] 
            self.response       = t[6] 
            self.content_len    = t[7] 
            self.content_type   = t[8] 
            self.server         = t[9]
            self.range          = str(t[10:-1])

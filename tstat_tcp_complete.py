#!/usr/bin/python

import decimal

conn_types = ['UNK', 'HTTP', 'RSTP', 'RTP', 'ICY', 'RTCP', 'MSN', 'YMSG', 'XMPP', 'P2P', 'SKYPE', 'SMTP', 'POP3', 'IMAP4', 'SSL', 'ED2K', 'SSH', 'RTMP', 'MSE/PE']

class tstatrecord:
    def __init__(self, line):
        t = line.split(' ')
        # C2S                           Short description 
        self.cip            = t[0]      #   Client/Server IP addr   -   IP addresses of the client/server
        self.cport          = t[1]      #   Client/Server TCP port  -   TCP port addresses for the client/server
        self.c2spckt        = t[2]      #   packets     -   total number of packets observed form the client/server
        self.cressent       = t[3]      #   RST sent    0/1     0 = no RST segment has been sent by the client/server
        self.cackssent      = t[4]      #   ACK sent    -   number of segments with the ACK field set to 1
        self.cpureackssent  = t[5]      #   PURE ACK sent   -   number of segments with ACK field set to 1 and no data
        self.csentbytes     = t[6]      #   unique bytes    bytes   number of bytes sent in the payload
        self.cdatapckt      = t[7]      #   data pkts   -   number of segments with payload
        self.ctxdata        = t[8]      #   data bytes  bytes   number of bytes transmitted in the payload, including retransmissions
        self.crtxpckt       = t[9]      #   rexmit pkts     -   number of retransmitted segments
        self.crtxdata       = t[10]     #    rexmit bytes    bytes   number of retransmitted bytes
        self.coutseqpckt    = t[11]     #    out seq pkts    -   number of segments observed out of sequence
        self.csynpckt       = t[12]     #    SYN count   -   number of SYN segments observed (including rtx)
        self.cfinpckt       = t[13]     #    FIN count   -   number of FIN segments observed (including rtx)
        self.cws            = t[14]     #    RFC1323 ws  0/1     Window scale option sent
        self.ctss           = t[15]     #    RFC1323 ts  0/1     Timestamp option sent
        self.cwsneg         = t[16]     #    window scale    -   Scaling values negotiated [scale factor]
        self.csackr         = t[17]     #    SACK req    0/1     SACK option set
        self.csacks         = t[18]     #    SACK sent   -   number of SACK messages sent
        self.cMssdec        = t[19]     #    MSS     bytes   MSS declared
        self.cMssmeas       = t[20]     #    max seg size    bytes   Maximum segment size observed
        self.cmssmeas       = t[21]     #    min seg size    bytes   Minimum segment size observed
        self.cMrw           = t[22]     #    win max     bytes   Maximum receiver window announced (already scale by the window scale factor)
        self.cmrw           = t[23]     #    win min     bytes   Maximum receiver windows announced (already scale by the window scale factor)
        self.cwz            = t[24]     #    win zero    -   Total number of segments declaring zero as receiver window
        self.cMwin          = t[25]     #    cwin max    bytes   Maximum in-flight-size computed as the difference between the largest sequence number so far, and the corresponding last ACK message on the reverse path. It is an estimate of the congestion window
        self.cmwin          = t[26]     #    cwin min    bytes   Minimum in-flight-size
        self.ciwin          = t[27]     #    initial cwin    bytes   First in-flight size, or total number of unack-ed bytes sent before receiving the first ACK segment
        self.c2savgrtt      = t[28]     #    Average rtt     ms  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK
        self.c2sminrtt      = t[29]     #    rtt min     ms  Minimum RTT observed during connection lifetime
        self.c2savgmaxrtt   = t[30]     #    rtt max     ms  Maximum RTT observed during connection lifetime
        self.c2sstdrtt      = t[31]     #    Stdev rtt   ms  Standard deviation of the RTT
        self.c2srttsamples  = t[32]     #    rtt count   -   Number of valid RTT observation
        self.c2sttlmin      = t[33]     #    ttl_min     -   Minimum Time To Live
        self.c2sttlmax      = t[34]     #    ttl_max     -   Maximum Time To Live
        self.c2srto         = t[35]     #    rtx RTO     -   Number of retransmitted segments due to timeout expiration
        self.c2srfr         = t[36]     #    rtx FR  -   Number of retransmitted segments due to Fast Retransmit (three dup-ack)
        self.c2sreord       = t[37]     #    reordering  -   Number of packet reordering observed
        self.c2sdup         = t[38]     #    net dup     -   Number of network duplicates observed
        self.c2sunk         = t[39]     #    unknown     -   Number of segments not in sequence or duplicate which are not classified as specific events
        self.c2cflcntl      = t[40]     #    flow control    -   Number of retransmitted segments to probe the receiver window
        self.c2sunnecrto    = t[41]     #    unnece rtx RTO  -   Number of unnecessary transmissions following a timeout expiration
        self.c2sunnecfr     = t[42]     #    unnece rtx FR   -   Number of unnecessary transmissions following a fast retransmit
        self.c2srsyn        = t[43]     #    != SYN seqno    0/1     1 = retransmitted SYN segments have different initial seqno
        # S2C                           Short description   Unit    Long description
        self.sip            = t[44]     # Client/Server IP addr   -   IP addresses of the client/server
        self.sport          = t[45]     # Client/Server TCP port  -   TCP port addresses for the client/server
        self.s2cpckt        = t[46]     # packets     -   total number of packets observed form the client/server
        self.sressent       = t[47]     # RST sent    0/1     0 = no RST segment has been sent by the client/server
        self.sackssent      = t[48]     # ACK sent    -   number of segments with the ACK field set to 1
        self.spureackssent  = t[49]     # PURE ACK sent   -   number of segments with ACK field set to 1 and no data
        self.ssentbytes     = t[50]     # unique bytes    bytes   number of bytes sent in the payload
        self.sdatapckt      = t[51]     # data pkts   -   number of segments with payload
        self.stxdata        = t[52]     # data bytes  bytes   number of bytes transmitted in the payload, including retransmissions
        self.srtxpckt       = t[53]     # rexmit pkts     -   number of retransmitted segments
        self.srtxdata       = t[54]     # rexmit bytes    bytes   number of retransmitted bytes
        self.soutseqpckt    = t[55]     # out seq pkts    -   number of segments observed out of sequence
        self.ssynpckt       = t[56]     # SYN count   -   number of SYN segments observed (including rtx)
        self.sfinpckt       = t[57]     # FIN count   -   number of FIN segments observed (including rtx)
        self.sws            = t[58]     # RFC1323 ws  0/1     Window scale option sent
        self.stss           = t[59]     # RFC1323 ts  0/1     Timestamp option sent
        self.swsneg         = t[60]     # window scale    -   Scaling values negotiated [scale factor]
        self.ssackr         = t[61]     # SACK req    0/1     SACK option set
        self.ssacks         = t[62]     # SACK sent   -   number of SACK messages sent
        self.sMssdec        = t[63]     # MSS     bytes   MSS declared
        self.sMssmeas       = t[64]     # max seg size    bytes   Maximum segment size observed
        self.smssmeas       = t[65]     # min seg size    bytes   Minimum segment size observed
        self.sMrw           = t[66]     # win max     bytes   Maximum receiver window announced (already scale by the window scale factor)
        self.smrw           = t[67]     # win min     bytes   Maximum receiver windows announced (already scale by the window scale factor)
        self.swz            = t[68]     # win zero    -   Total number of segments declaring zero as receiver window
        self.sMwin          = t[69]     # cwin max    bytes   Maximum in-flight-size computed as the difference between the largest sequence number so far, and the corresponding last ACK message on the reverse path. It is an estimate of the congestion window
        self.smwin          = t[70]     # cwin min    bytes   Minimum in-flight-size
        self.siwin          = t[71]     # initial cwin    bytes   First in-flight size, or total number of unack-ed bytes sent before receiving the first ACK segment
        self.s2cavgrtt      = t[72]     # Average rtt     ms  Average RTT computed measuring the time elapsed between the data segment and the corresponding ACK
        self.s2cminrtt      = t[73]     # rtt min     ms  Minimum RTT observed during connection lifetime
        self.s2cavgmaxrtt   = t[74]     # rtt max     ms  Maximum RTT observed during connection lifetime
        self.s2cstdrtt      = t[75]     # Stdev rtt   ms  Standard deviation of the RTT
        self.s2crttsamples  = t[76]     # rtt count   -   Number of valid RTT observation
        self.s2cttlmin      = t[77]     # ttl_min     -   Minimum Time To Live
        self.s2cttlmax      = t[78]     # ttl_max     -   Maximum Time To Live
        self.s2crto         = t[79]     # rtx RTO     -   Number of retransmitted segments due to timeout expiration
        self.s2crfr         = t[80]     # rtx FR  -   Number of retransmitted segments due to Fast Retransmit (three dup-ack)
        self.s2creord       = t[81]     # reordering  -   Number of packet reordering observed
        self.s2cdup         = t[82]     # net dup     -   Number of network duplicates observed
        self.s2cunk         = t[83]     # unknown     -   Number of segments not in sequence or duplicate which are not classified as specific events
        self.s2cflcntl      = t[84]     # flow control    -   Number of retransmitted segments to probe the receiver window
        self.s2cunnecrto    = t[85]     # unnece rtx RTO  -   Number of unnecessary transmissions following a timeout expiration
        self.s2cunnecfr     = t[86]     # unnece rtx FR   -   Number of unnecessary transmissions following a fast retransmit
        self.s2crsyn        = t[87]     # != SYN seqno    0/1     1 = retransmitted SYN segments have different initial seqno
        # Further flow features
        self.comlp          = t[88]         # Completion time     ms  Flow duration since first packet to last packet
        self.fpckt          = t[89]         # First time  ms  Flow first packet since first segment ever
        self.lpckt          = t[90]         # Last time   ms  Flow last segment since first segment ever
        self.cfpckt         = t[91]         # C first payload     ms  Client first segment with payload since the first flow segment
        self.sfpckt         = t[92]         # S first payload     ms  Server first segment with payload since the first flow segment
        self.clpckt         = t[93]         # C last payload  ms  Client last segment with payload since the first flow segment
        self.slpckt         = t[94]         # S last payload  ms  Server last segment with payload since the first flow segment
        self.cfack          = t[95]         # C first ack     ms  Client first ACK segment (without SYN) since the first flow segment
        self.sfack          = t[96]         # S first ack     ms  Server first ACK segment (without SYN) since the first flow segment
        self.timestamp      = t[97]         # First time abs  ms  Flow first packet absolute time (epoch)
        self.cipint         = t[98]         # C Internal  0/1     1 = client has internal IP, 0 = client has external IPself.                = t[
        self.sipint         = t[99]         # S Internal  0/1     1 = server has internal IP, 0 = server has external IP
        if len(t) == 119:
            self.fqdn           = t[-8:-5]      # Fully qualified domain name 
            self.fqdnr          = t[-1][:-1]    # Reversed fqdn
        else:
            self.fqdn       = None
            self.fqdnr      = ''
        self.conntype       = t[100]        # Bitmask stating the connection type as identified by TCPL7 inspection engine (see protocol.h)
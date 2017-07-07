#!/usr/bin/env python2

# Copyright 2013-present Barefoot Networks, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from mininet.net import Mininet
from mininet.topo import Topo
from mininet.node import OVSKernelSwitch
from mininet.log import setLogLevel, info
from mininet.cli import CLI
from mininet.util import dumpNetConnections
from p4_mininet import P4Switch, P4Host

import argparse
from time import sleep

parser = argparse.ArgumentParser(description='Mininet demo')
parser.add_argument('--behavioral-exe', help='Path to behavioral executable',
                    type=str, action="store", required=True)
parser.add_argument('--thrift-port', help='Thrift server port for table updates',
                    type=int, action="store", default=9090)
parser.add_argument('--num-senders', help='Number of senders to connect to switch',
                    type=int, action="store", default=2)
parser.add_argument('--num-rcvrs', help='Number of receivers to connect to switch',
                    type=int, action="store", default=2)
parser.add_argument('--mode', choices=['l2', 'l3'], type=str, default='l3')
parser.add_argument('--json', help='Path to JSON config file',
                    type=str, action="store", required=True)
parser.add_argument('--pcap-dump', help='Dump packets on interfaces to pcap files',
                    type=str, action="store", required=False, default=False)

args = parser.parse_args()

class DemoSwitch(P4Switch):
    """ Demo switch that can hot-swap one query JSON for another. """
    def __init__(self, 
                 name, 
                 sw_path = None, 
                 json_path = None, 
                 thrift_port = None, 
                 pcap_dump = None, 
                 **kwargs):
        P4Switch.__init__(self, name,
                          sw_path = sw_path,
                          json_path = json_path,
                          thrift_port = thrift_port,
                          pcap_dump = pcap_dump,
                          **kwargs)

    def restart(self, json_path):
        """Restart a new P4 switch with the new JSON"""
        print "Stopping P4 switch", self.name
        """ Execute part of the stop() routine. """
        self.output.flush()
        self.cmd('kill %' + self.sw_path)
        self.cmd('wait')
        """ Now re-run part of the start() routine that constructs a new switch
        path with the new JSON argument. """
        self.json_path = json_path
        args = [self.sw_path]
        # args.extend( ['--name', self.name] )
        # args.extend( ['--dpid', self.dpid] )
        for port, intf in self.intfs.items():
            if not intf.IP():
                args.extend( ['-i', str(port) + "@" + intf.name] )
        if self.pcap_dump:
            args.append("--pcap")
            # args.append("--useFiles")
        if self.thrift_port:
            args.extend( ['--thrift-port', str(self.thrift_port)] )
        if self.nanomsg:
            args.extend( ['--nanolog', self.nanomsg] )
        args.extend( ['--device-id', str(self.device_id)] )
        # P4Switch.device_id += 1
        args.append(self.json_path)
        if self.enable_debugger:
            args.append("--debugger")
        logfile = '/tmp/p4s.%s.log' % self.name
        print ' '.join(args)

        self.cmd( ' '.join(args) + ' >' + logfile + ' 2>&1 &' )
        # self.cmd( ' '.join(args) + ' > /dev/null 2>&1 &' )

        print "switch has been restarted"

class DiamondTopo(Topo):
    "Single switch connected to n (< 256) hosts."
    def __init__(self, sw_path, json_path, thrift_port, pcap_dump, num_senders, num_rcvrs, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)

        s1 = self.addSwitch('s1',
                             sw_path = sw_path,
                             json_path = json_path,
                             thrift_port = thrift_port,
                             pcap_dump = pcap_dump)
        
        s2 = self.addSwitch('s2',
                             sw_path = sw_path,
                             json_path = json_path,
                             thrift_port = thrift_port + 1,
                             pcap_dump = pcap_dump)
        
        s3 = self.addSwitch('s3',
                             sw_path = sw_path,
                             json_path = json_path,
                             thrift_port = thrift_port + 2,
                             pcap_dump = pcap_dump)
        
        s4 = self.addSwitch('s4',
                             sw_path = sw_path,
                             json_path = json_path,
                             thrift_port = thrift_port + 3,
                             pcap_dump = pcap_dump) 

        for h in xrange(num_senders):
            host = self.addHost('h%d' % (h + 1),
                                ip = "10.0.%d.10/24" % h,
                                mac = '00:04:00:00:00:%02x' % h)
            self.addLink(host, s1)

        for h in xrange(num_rcvrs):
            n = h + num_senders
            host = self.addHost('h%d' % (n + 1),
                                ip = "10.0.%d.10/24" % n,
                                mac = '00:04:00:00:00:%02x' % n)
            self.addLink(host, s4)
            
        self.addLink(s1, s2)
        self.addLink(s1, s3)
        self.addLink(s2, s4)
        self.addLink(s3, s4)

def main():
    mode = args.mode

    topo = DiamondTopo(args.behavioral_exe,
                            args.json,
                            args.thrift_port,
                            args.pcap_dump,
                            args.num_senders,
                            args.num_rcvrs)
    net = Mininet(topo = topo,
                  host = P4Host,
                  switch = P4Switch,
                  controller = None)
    net.start()

    # takes in switch ID and port
    def mac(i, j):
        return "00:aa:bb:00:%02x:%02x" % (i-1,j)
    # takes in switch ID
    def sw_ip(i):
        return "10.%d.0.1" % (i)

    num_senders = args.num_senders
    num_rcvrs = args.num_rcvrs
    sw_mac = [mac(1,n) for n in xrange(num_senders)]
    sw_addr = ["10.0.%d.1" % n for n in xrange(num_senders)]

    sw_mac2 = [mac(4,n) for n in xrange(num_rcvrs)]
    sw_addr2 = ["10.0.%d.1" % (n+num_senders) for n in xrange(num_rcvrs)]
    print 'Connecting hosts to s1...'

    # Connect all hosts to s1
    for n in xrange(num_senders):
        h = net.get('h%d' % (n + 1))
        h.setARP(sw_addr[n], sw_mac[n])
        h.setDefaultRoute("dev eth0 via %s" % sw_addr[n])
    
    for n in xrange(num_rcvrs):
        h = net.get('h%d' % (num_rcvrs + n))
        h.setARP(sw_addr2[n], sw_mac2[n])
        h.setDefaultRoute("dev eth0 via %s" % sw_addr2[n])

    net.get('s1').setARP(sw_ip(2), mac(2, 1))
    net.get('s1').setARP(sw_ip(3), mac(3,1))
    net.get('s2').setARP(sw_ip(1), mac(1, num_senders))
    net.get('s2').setARP(sw_ip(4), mac(4, num_rcvrs))
    net.get('s3').setARP(sw_ip(1), mac(1, num_senders+1))
    net.get('s3').setARP(sw_ip(4), mac(4, num_rcvrs+1))
    net.get('s4').setARP(sw_ip(2), mac(2, 2))
    net.get('s4').setARP(sw_ip(3), mac(3,2))

    sleep(1)
    dumpNetConnections(net)
    print "Ready !"

    CLI( net )
    net.stop()

if __name__ == '__main__':
    setLogLevel( 'info' )
    main()

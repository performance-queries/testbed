from scapy.all import Ether, IP, TCP, sendp, Raw
import random

# Generate traffic from random source IPs to destinations:
# x.x.i.j, with j packets to each such destination.
count = 0
for i in xrange(5):
    for j in xrange(5):
        for k in xrange(1):
            if count % 1000 == 0 and count >= 1000:
                print "%d packets sent" % count
            #src = "%d.%d.%d.%d" % (random.randint(0,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))  
            src = "%d.%d.%d.%d" % (1,2,3,4)
            p = Ether() / IP(src=src, dst="1.2.%d.%d" % (1, j+1), ttl=10) / TCP() / Raw(load='x' * (j+1))
            sendp(p, iface="veth3", verbose=False)
            print len(p)
            count = count + 1
print "%d packets sent" % count
